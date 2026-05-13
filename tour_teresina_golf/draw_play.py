"""Desenho do campo, HUD e miras."""

from __future__ import annotations

import math
from pathlib import Path

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
    DEBUG_DRAW_PHASE_COLLISIONS,
    HOLE_CAPTURE_RADIUS,
    MAX_DRAG_LEN,
)
from tour_teresina_golf.level import Level
from tour_teresina_golf.play_round import RoundSession, calc_stars

_REPO_ROOT = Path(__file__).resolve().parent.parent
_FLAG_SCALED_CACHE: dict[tuple[str, int], pygame.Surface] = {}


def _scaled_flag_surface(path: Path, target_h: int) -> pygame.Surface | None:
    key = (str(path.resolve()), target_h)
    if key in _FLAG_SCALED_CACHE:
        return _FLAG_SCALED_CACHE[key]
    if not path.is_file():
        return None
    img = pygame.image.load(str(path)).convert_alpha()
    iw, ih = img.get_size()
    if ih <= 0:
        return None
    scale = target_h / ih
    nw = max(1, int(round(iw * scale)))
    surf = pygame.transform.smoothscale(img, (nw, target_h))
    _FLAG_SCALED_CACHE[key] = surf
    return surf


def draw_playfield(surface: pygame.Surface, level: Level) -> None:
    """Fairway procedural ou imagem de fundo; colisões opcionais visíveis em debug."""
    if level.background is not None:
        surface.blit(level.background, (0, 0))
    elif level.play_rect:
        pr = level.play_rect
        pygame.draw.rect(surface, COLOR_FAIRWAY, pr)
        for i in range(0, pr.w, 40):
            for j in range(0, pr.h, 40):
                if (i // 40 + j // 40) % 2 == 0:
                    pygame.draw.rect(surface, COLOR_FAIRWAY_ALT, (pr.x + i, pr.y + j, 40, 40))
        pygame.draw.rect(surface, COLOR_ASPHALT, pr, width=3)

    if not level.hide_solids_overlay:
        for w in level.walls:
            pygame.draw.rect(surface, COLOR_WALL, w)
            pygame.draw.rect(surface, (45, 38, 36), w, width=2)

        for r in level.water:
            pygame.draw.rect(surface, COLOR_WATER, r)
            pygame.draw.rect(surface, COLOR_WATER_SHALLOW, r.inflate(-6, -6), border_radius=4)

        for o in level.obstacles:
            pygame.draw.rect(surface, (34, 78, 46), o)
            pygame.draw.rect(surface, (28, 62, 38), o, width=2)

    # Com bitmap + overlay oculto não desenhar anel aqui (arte já tem terreno); buraco
    # “real” pode vir de ``draw_programmatic_hole_and_flag`` quando definido no nível.
    art_only_hole = level.background is not None and level.hide_solids_overlay
    if not art_only_hole:
        hx, hy = level.hole_center
        cap = level.hole_capture_radius if level.hole_capture_radius is not None else HOLE_CAPTURE_RADIUS
        ri = int(cap)
        pygame.draw.circle(surface, COLOR_HOLE_RING, (int(hx), int(hy)), ri + 3, width=3)
        pygame.draw.circle(surface, COLOR_HOLE, (int(hx), int(hy)), max(4, ri - 4))

    if DEBUG_DRAW_PHASE_COLLISIONS:
        if level.collision_debug_overlay is not None:
            surface.blit(level.collision_debug_overlay, (0, 0))
        else:
            for r in level.walls + level.obstacles:
                pygame.draw.rect(surface, (255, 0, 0), r, 2)


def draw_programmatic_hole_and_flag(surface: pygame.Surface, level: Level) -> None:
    """Círculo do buraco + sprite da bandeira (base do mastro no centro do buraco)."""
    if not level.draw_programmatic_hole:
        return
    hx, hy = level.hole_center
    cap = level.hole_capture_radius if level.hole_capture_radius is not None else HOLE_CAPTURE_RADIUS
    ri = int(cap)
    pygame.draw.circle(surface, COLOR_HOLE_RING, (int(hx), int(hy)), ri + 3, width=3)
    pygame.draw.circle(surface, COLOR_HOLE, (int(hx), int(hy)), max(4, ri - 4))

    flag_path = level.flag_sprite_path or (_REPO_ROOT / "acessorios" / "bandeira.png")
    target_h = max(55, min(72, BALL_RADIUS * 9))
    flag = _scaled_flag_surface(flag_path, target_h)
    if flag is not None:
        fw, fh = flag.get_size()
        surface.blit(flag, (int(hx - fw // 2), int(hy - fh)))


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


def _star_outer_radius_px(font: pygame.font.Font) -> int:
    h = max(font.get_height(), font.get_linesize())
    return max(7, int(h * 0.38))


def _five_point_star_points(cx: float, cy: float, outer: float) -> list[tuple[int, int]]:
    inner = outer * 0.42
    pts: list[tuple[int, int]] = []
    for i in range(10):
        ang = -math.pi / 2 + i * (math.pi / 5)
        rad = outer if i % 2 == 0 else inner
        pts.append((int(cx + math.cos(ang) * rad), int(cy + math.sin(ang) * rad)))
    return pts


def _draw_star_shape(
    surface: pygame.Surface,
    cx: int,
    cy: int,
    outer_r: int,
    *,
    filled: bool,
    fill_color: tuple[int, int, int],
    outline_color: tuple[int, int, int],
) -> None:
    pts = _five_point_star_points(float(cx), float(cy), float(outer_r))
    w_line = max(1, outer_r // 5)
    if filled:
        pygame.draw.polygon(surface, fill_color, pts)
        pygame.draw.polygon(
            surface,
            (min(255, fill_color[0] + 35), min(255, fill_color[1] + 25), min(255, fill_color[2] + 20)),
            pts,
            width=1,
        )
    else:
        pygame.draw.polygon(surface, outline_color, pts, width=w_line)


def draw_stars(surface: pygame.Surface, font: pygame.font.Font, stars: int, center_x: int, y: int) -> None:
    """Três estrelas (polígono) centradas em center_x; `stars` (1–3) é limitado a esse intervalo."""
    n = min(3, max(1, int(stars)))
    outer = _star_outer_radius_px(font)
    gap = max(4, outer // 3)
    slot = 2 * outer + gap
    total_w = 3 * slot - gap
    x0 = center_x - total_w // 2 + outer
    cy = y + outer + 2
    gold = (255, 214, 80)
    dim = (100, 90, 60)
    for i in range(3):
        _draw_star_shape(surface, x0 + i * slot, cy, outer, filled=i < n, fill_color=gold, outline_color=dim)


def draw_hud(surface: pygame.Surface, font: pygame.font.Font, session: RoundSession) -> None:
    """Painel único no canto superior esquerdo (evita sobrepor tacadas com nome da fase)."""
    pad = 12
    inner = 10
    gap = 5
    line1 = f"Tacadas restantes: {session.strokes_left}"
    line2 = f"Fase: {session.level.name}"
    t_left = font.render(line1, True, COLOR_UI_TEXT)
    t_phase = font.render(line2, True, COLOR_UI_ACCENT)
    if session.strokes_left == 0 and not session.hole_victory_ready():
        preview_fill = 0
    else:
        preview_fill = calc_stars(session.strokes_left)
    t_rank_label = font.render("Ranking atual: ", True, COLOR_UI_ACCENT)
    outer = _star_outer_radius_px(font)
    gap = max(4, outer // 3)
    slot = 2 * outer + gap
    stars_w = 3 * slot - gap
    line3_w = t_rank_label.get_width() + stars_w
    line3_h = max(t_rank_label.get_height(), 2 * outer + 4)
    bw = max(t_left.get_width(), t_phase.get_width(), line3_w) + inner * 2
    bh = t_left.get_height() + gap + t_phase.get_height() + gap + line3_h + inner * 2
    bg = pygame.Surface((bw, bh), pygame.SRCALPHA)
    bg.fill((16, 14, 22, 228))
    pygame.draw.rect(bg, (90, 82, 100), bg.get_rect(), width=1, border_radius=6)
    surface.blit(bg, (pad, pad))
    surface.blit(t_left, (pad + inner, pad + inner))
    surface.blit(t_phase, (pad + inner, pad + inner + t_left.get_height() + gap))
    y3 = pad + inner + t_left.get_height() + gap + t_phase.get_height() + gap
    label_y = y3 + (line3_h - t_rank_label.get_height()) // 2
    surface.blit(t_rank_label, (pad + inner, label_y))
    gold = (255, 214, 80)
    dim = (100, 90, 60)
    x0 = pad + inner + t_rank_label.get_width() + outer
    cy = y3 + line3_h // 2
    for i in range(3):
        _draw_star_shape(surface, x0 + i * slot, cy, outer, filled=i < preview_fill, fill_color=gold, outline_color=dim)


def draw_pause_overlay(
    surface: pygame.Surface,
    font_title: pygame.font.Font,
    font_ui: pygame.font.Font,
    btn_continuar: pygame.Rect,
    btn_menu: pygame.Rect,
) -> None:
    veil = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    veil.fill((10, 10, 20, 172))
    surface.blit(veil, (0, 0))

    cx = surface.get_width() // 2
    cy = surface.get_height() // 2

    t = font_title.render("PAUSADO", True, (230, 240, 255))
    surface.blit(t, t.get_rect(center=(cx, cy - 56)))

    for rect, label in (
        (btn_continuar, "Continuar"),
        (btn_menu, "Sair para o Menu"),
    ):
        pygame.draw.rect(surface, (38, 52, 72), rect, border_radius=8)
        pygame.draw.rect(surface, (100, 130, 180), rect, width=2, border_radius=8)
        tx = font_ui.render(label, True, (220, 230, 255))
        surface.blit(tx, tx.get_rect(center=rect.center))
