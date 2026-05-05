"""Colisão círculo vs retângulos alinhados aos eixos."""

from __future__ import annotations

import math

import pygame

from tour_teresina_golf.config import RESTITUTION


def _clamp(v: float, lo: float, hi: float) -> float:
    return lo if v < lo else hi if v > hi else v


def resolve_circle_rect(
    x: float,
    y: float,
    vx: float,
    vy: float,
    r: float,
    rect: pygame.Rect,
) -> tuple[float, float, float, float, bool]:
    """
    Resolve penetração da bola com um AABB; devolve nova posição e velocidade.
    Retorna também hit (houve colisão neste passo).
    """
    left = float(rect.left)
    top = float(rect.top)
    right = float(rect.right)
    bottom = float(rect.bottom)

    cx = _clamp(x, left, right)
    cy = _clamp(y, top, bottom)
    dx = x - cx
    dy = y - cy
    dist_sq = dx * dx + dy * dy
    r_sq = r * r

    if dist_sq >= r_sq:
        return x, y, vx, vy, False

    if dist_sq < 1e-10:
        # Centro dentro ou no vértice: empurra pela menor penetração nas quatro faces
        dl = x - left
        dr = right - x
        dt = y - top
        db = bottom - y
        m = min(dl, dr, dt, db)
        if m == dl:
            nx, ny, pen = -1.0, 0.0, r + dl
        elif m == dr:
            nx, ny, pen = 1.0, 0.0, r + dr
        elif m == dt:
            nx, ny = 0.0, -1.0
            pen = r + dt
        else:
            nx, ny = 0.0, 1.0
            pen = r + db
        x += nx * pen
        y += ny * pen
        vn = vx * nx + vy * ny
        if vn < 0:
            vx -= (1.0 + RESTITUTION) * vn * nx
            vy -= (1.0 + RESTITUTION) * vn * ny
        return x, y, vx, vy, True

    dist = math.sqrt(dist_sq)
    nx = dx / dist
    ny = dy / dist
    penetration = r - dist
    x += nx * penetration
    y += ny * penetration

    vn = vx * nx + vy * ny
    if vn < 0:
        vx -= (1.0 + RESTITUTION) * vn * nx
        vy -= (1.0 + RESTITUTION) * vn * ny

    return x, y, vx, vy, True


def collide_ball_all_rects(
    x: float,
    y: float,
    vx: float,
    vy: float,
    r: float,
    rects: list[pygame.Rect],
    iterations: int = 3,
) -> tuple[float, float, float, float]:
    """Várias iterações para reduzir tuneling."""
    for _ in range(iterations):
        hit_any = False
        for rect in rects:
            x, y, vx, vy, hit = resolve_circle_rect(x, y, vx, vy, r, rect)
            hit_any = hit_any or hit
        if not hit_any:
            break
    return x, y, vx, vy


def speed_sq(vx: float, vy: float) -> float:
    return vx * vx + vy * vy


def ball_center_in_water(x: float, y: float, water: list[pygame.Rect]) -> bool:
    for z in water:
        if z.collidepoint(x, y):
            return True
    return False
