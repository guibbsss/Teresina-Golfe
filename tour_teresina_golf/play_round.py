"""Uma tacada / estado da bola na fase atual."""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum, auto

import pygame

from tour_teresina_golf import audio_stub
from tour_teresina_golf.collision import (
    ball_center_in_water,
    circle_overlaps_collision_grid,
    collide_ball_all_rects,
    collide_ball_bitmap,
)
from tour_teresina_golf.config import (
    AIM_GRAB_RADIUS,
    BALL_RADIUS,
    HOLE_CAPTURE_RADIUS,
    HOLE_WIN_SPEED_SQ,
    MAX_DRAG_LEN,
    MAX_SHOT_SPEED,
    MIN_DRAG_SHOT,
)
from tour_teresina_golf.level import Level
from tour_teresina_golf.physics import apply_friction, clamp_speed, is_stopped


class RoundOutcome(Enum):
    NONE = auto()
    VICTORY = auto()
    GAME_OVER_WATER = auto()
    GAME_OVER_STROKES = auto()
    WATER_RESPAWN = auto()


def _speed_sq(vx: float, vy: float) -> float:
    return vx * vx + vy * vy


@dataclass
class RoundSession:
    level: Level
    strokes_left: int
    ball_x: float
    ball_y: float
    ball_vx: float
    ball_vy: float
    rolling: bool
    aiming: bool
    aim_anchor_x: float
    aim_anchor_y: float

    @classmethod
    def new(cls, level: Level) -> RoundSession:
        x, y = level.ball_spawn
        return cls(
            level=level,
            strokes_left=level.strokes,
            ball_x=float(x),
            ball_y=float(y),
            ball_vx=0.0,
            ball_vy=0.0,
            rolling=False,
            aiming=False,
            aim_anchor_x=float(x),
            aim_anchor_y=float(y),
        )

    def reset_level(self) -> None:
        x, y = self.level.ball_spawn
        self.ball_x = float(x)
        self.ball_y = float(y)
        self.ball_vx = 0.0
        self.ball_vy = 0.0
        self.rolling = False
        self.aiming = False
        self.strokes_left = self.level.strokes

    def respawn_at_spawn_keep_strokes(self) -> None:
        """Repor a bola no spawn sem reiniciar tacadas (ex.: água na fase 3)."""
        x, y = self.level.ball_spawn
        self.ball_x = float(x)
        self.ball_y = float(y)
        self.ball_vx = 0.0
        self.ball_vy = 0.0
        self.rolling = False
        self.aiming = False

    def all_solids(self) -> list[pygame.Rect]:
        return list(self.level.walls) + list(self.level.obstacles)

    def _check_hole_victory(self) -> bool:
        hx, hy = self.level.hole_center
        dx = self.ball_x - hx
        dy = self.ball_y - hy
        cap = self.level.hole_capture_radius if self.level.hole_capture_radius is not None else HOLE_CAPTURE_RADIUS
        if dx * dx + dy * dy > cap * cap:
            return False
        win_sq = self.level.hole_win_speed_sq if self.level.hole_win_speed_sq is not None else HOLE_WIN_SPEED_SQ
        return _speed_sq(self.ball_vx, self.ball_vy) < win_sq

    def physics_step(self, dt: float) -> RoundOutcome:
        self.ball_x += self.ball_vx * dt
        self.ball_y += self.ball_vy * dt

        cg = self.level.collision_grid
        if cg is not None:
            bx, by, bvx, bvy = collide_ball_bitmap(
                self.ball_x,
                self.ball_y,
                self.ball_vx,
                self.ball_vy,
                BALL_RADIUS,
                cg,
            )
        else:
            bx, by, bvx, bvy = collide_ball_all_rects(
                self.ball_x,
                self.ball_y,
                self.ball_vx,
                self.ball_vy,
                BALL_RADIUS,
                self.all_solids(),
            )
        self.ball_x, self.ball_y = bx, by
        self.ball_vx, self.ball_vy = bvx, bvy

        wg = self.level.water_grid
        if wg is not None and circle_overlaps_collision_grid(
            wg, self.ball_x, self.ball_y, BALL_RADIUS, 16
        ):
            audio_stub.play_water_splash()
            self.respawn_at_spawn_keep_strokes()
            return RoundOutcome.WATER_RESPAWN

        if ball_center_in_water(self.ball_x, self.ball_y, self.level.water):
            audio_stub.play_water_splash()
            self.rolling = False
            return RoundOutcome.GAME_OVER_WATER

        self.ball_vx, self.ball_vy = apply_friction(self.ball_vx, self.ball_vy, dt)
        self.ball_vx, self.ball_vy = clamp_speed(self.ball_vx, self.ball_vy)

        if self._check_hole_victory():
            self.ball_vx = 0.0
            self.ball_vy = 0.0
            self.rolling = False
            return RoundOutcome.VICTORY

        if is_stopped(self.ball_vx, self.ball_vy):
            self.ball_vx = 0.0
            self.ball_vy = 0.0
            self.rolling = False
            return self._idle_outcome()
        return RoundOutcome.NONE

    def _idle_outcome(self) -> RoundOutcome:
        hx, hy = self.level.hole_center
        dx = self.ball_x - hx
        dy = self.ball_y - hy
        dist_sq = dx * dx + dy * dy
        cap = self.level.hole_capture_radius if self.level.hole_capture_radius is not None else HOLE_CAPTURE_RADIUS
        if dist_sq <= cap * cap:
            return RoundOutcome.VICTORY
        if self.strokes_left <= 0:
            return RoundOutcome.GAME_OVER_STROKES
        return RoundOutcome.NONE

    def try_begin_aim(self, mx: float, my: float) -> None:
        if self.rolling or self.strokes_left <= 0:
            return
        dx = mx - self.ball_x
        dy = my - self.ball_y
        if dx * dx + dy * dy <= AIM_GRAB_RADIUS * AIM_GRAB_RADIUS:
            self.aiming = True
            self.aim_anchor_x = self.ball_x
            self.aim_anchor_y = self.ball_y
            audio_stub.play_slingshot_pull()

    def release_shot(self, mx: float, my: float) -> None:
        if not self.aiming:
            return
        self.aiming = False
        drag_x = mx - self.aim_anchor_x
        drag_y = my - self.aim_anchor_y
        length = math.hypot(drag_x, drag_y)
        if length <= MIN_DRAG_SHOT:
            return

        t = min(length, MAX_DRAG_LEN)
        span = MAX_DRAG_LEN - MIN_DRAG_SHOT
        if span <= 0:
            return
        speed_mag = ((t - MIN_DRAG_SHOT) / span) * MAX_SHOT_SPEED
        nx = -drag_x / length
        ny = -drag_y / length
        self.ball_vx = nx * speed_mag
        self.ball_vy = ny * speed_mag
        self.ball_vx, self.ball_vy = clamp_speed(self.ball_vx, self.ball_vy)
        self.rolling = True
        self.strokes_left -= 1
        audio_stub.play_shot()

    def cancel_aim(self) -> None:
        self.aiming = False
