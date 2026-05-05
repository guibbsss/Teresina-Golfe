"""Desenho do campo, HUD e miras."""

from __future__ import annotations

import math

import pygame

from tour_teresina_golf.config import (
    BALL_RADIUS,
    COLOR_ASPHALT,
    COLOR_BALL,
    COLOR_FAIRWAY,
    COLOR_FAIRWAY_ALT,
    COLOR_HOLE,
    COLOR_HOLE_RING,
    COLOR_UI_ACCENT,
    COLOR_UI_TEXT,
    COLOR_WALL,
    COLOR_WATER,
    COLOR_WATER_SHALLOW,
    HOLE_CAPTURE_RADIUS,
    MAX_DRAG_LEN,
)
from tour_teresina_golf.level import Level
from tour_teresina_golf.play_round import RoundSession


def draw_playfield(surface: pygame.Surface, level: Level) -> None:
    """Piso estilo fairway + faixa de asfalto nas bordas internas."""
    if level.play_rect:
        pr = level.play_rect
        pygame.draw.rect(surface, COLOR_FAIRWAY, pr)
        for i in range(0, pr.w, 40):
            for j in range(0, pr.h, 40):
                if (i // 40 + j // 40) % 2 == 0:
                    pygame.draw.rect(surface, COLOR_FAIRWAY_ALT, (pr.x + i, pr.y + j, 40, 40))
        pygame.draw.rect(surface, COLOR_ASPHALT, pr, width=3)

    for w in level.walls:
        pygame.draw.rect(surface, COLOR_WALL, w)
        pygame.draw.rect(surface, (45, 38, 36), w, width=2)

    for r in level.water:
        pygame.draw.rect(surface, COLOR_WATER, r)
        pygame.draw.rect(surface, COLOR_WATER_SHALLOW, r.inflate(-6, -6), border_radius=4)

    for o in level.obstacles:
        pygame.draw.rect(surface, (34, 78, 46), o)
        pygame.draw.rect(surface, (28, 62, 38), o, width=2)

    hx, hy = level.hole_center
    pygame.draw.circle(surface, COLOR_HOLE_RING, (int(hx), int(hy)), HOLE_CAPTURE_RADIUS + 3, width=3)
    pygame.draw.circle(surface, COLOR_HOLE, (int(hx), int(hy)), HOLE_CAPTURE_RADIUS - 4)


def draw_ball(surface: pygame.Surface, x: float, y: float) -> None:
    shadow = pygame.Surface((BALL_RADIUS * 4, BALL_RADIUS * 4), pygame.SRCALPHA)
    pygame.draw.circle(shadow, (0, 0, 0, 70), (BALL_RADIUS * 2, BALL_RADIUS * 2), BALL_RADIUS + 2)
    surface.blit(shadow, (int(x - BALL_RADIUS * 2 + 2), int(y - BALL_RADIUS * 2 + 3)))
    pygame.draw.circle(surface, COLOR_BALL, (int(x), int(y)), BALL_RADIUS)
    pygame.draw.circle(surface, (210, 210, 210), (int(x - 2), int(y - 2)), max(2, BALL_RADIUS // 4))


def draw_aim(surface: pygame.Surface, session: RoundSession, mouse_pos: tuple[int, int]) -> None:
    if not session.aiming:
        return
    mx, my = float(mouse_pos[0]), float(mouse_pos[1])
    ax, ay = session.aim_anchor_x, session.aim_anchor_y
    dx = mx - ax
    dy = my - ay
    dist = math.hypot(dx, dy)
    if dist < 1e-3:
        return
    drag_len = min(dist, MAX_DRAG_LEN)
    ux = dx / dist
    uy = dy / dist
    shot_len = drag_len * 1.15
    sx = ax - ux * shot_len
    sy = ay - uy * shot_len
    pygame.draw.line(surface, (255, 240, 200), (int(ax), int(ay)), (int(sx), int(sy)), width=3)
    for i in range(8):
        t = i / 7.0
        px = ax + (sx - ax) * t
        py = ay + (sy - ay) * t
        pygame.draw.circle(surface, (255, 220, 140), (int(px), int(py)), 3)


def draw_hud(surface: pygame.Surface, font: pygame.font.Font, session: RoundSession) -> None:
    """Painel único no canto superior esquerdo (evita sobrepor tacadas com nome da fase)."""
    pad = 12
    inner = 10
    gap = 5
    line1 = f"Tacadas restantes: {session.strokes_left}"
    line2 = f"Fase: {session.level.name}"
    t_left = font.render(line1, True, COLOR_UI_TEXT)
    t_phase = font.render(line2, True, COLOR_UI_ACCENT)
    bw = max(t_left.get_width(), t_phase.get_width()) + inner * 2
    bh = t_left.get_height() + gap + t_phase.get_height() + inner * 2
    bg = pygame.Surface((bw, bh), pygame.SRCALPHA)
    bg.fill((16, 14, 22, 228))
    pygame.draw.rect(bg, (90, 82, 100), bg.get_rect(), width=1, border_radius=6)
    surface.blit(bg, (pad, pad))
    surface.blit(t_left, (pad + inner, pad + inner))
    surface.blit(t_phase, (pad + inner, pad + inner + t_left.get_height() + gap))
