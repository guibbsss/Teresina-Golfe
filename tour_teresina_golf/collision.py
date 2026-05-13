"""Colisão círculo vs retângulos alinhados aos eixos e vs mapa bitmap."""

from __future__ import annotations

import math
from dataclasses import dataclass

import pygame

from tour_teresina_golf.config import RESTITUTION


@dataclass(frozen=True)
class CollisionGrid:
    """Mapa lógico: branco=0 (livre), sólido≠0; linha a linha y major, x minor."""

    width: int
    height: int
    solid: bytes

    def is_solid_px(self, xi: int, yi: int) -> bool:
        if xi < 0 or yi < 0 or xi >= self.width or yi >= self.height:
            return True
        return self.solid[yi * self.width + xi] != 0


def _solid_world(grid: CollisionGrid, x: float, y: float) -> bool:
    xi = int(x)
    yi = int(y)
    return grid.is_solid_px(xi, yi)


def circle_overlaps_collision_grid(
    grid: CollisionGrid, x: float, y: float, r: float, n_samples: int = 16
) -> bool:
    """True se o círculo (centro, raio) intersecta qualquer pixel marcado na grelha."""
    return _circle_overlaps_bitmap(grid, x, y, r, n_samples)


def _circle_overlaps_bitmap(grid: CollisionGrid, x: float, y: float, r: float, n_samples: int) -> bool:
    if _solid_world(grid, x, y):
        return True
    step = (2.0 * math.pi) / float(n_samples)
    for i in range(n_samples):
        a = i * step
        ca = math.cos(a)
        sa = math.sin(a)
        if _solid_world(grid, x + ca * r, y + sa * r):
            return True
    return False


def _escape_normal_bitmap(grid: CollisionGrid, x: float, y: float, r: float, n_samples: int) -> tuple[float, float]:
    nx_acc = 0.0
    ny_acc = 0.0
    step = (2.0 * math.pi) / float(n_samples)
    for i in range(n_samples):
        a = i * step
        ca = math.cos(a)
        sa = math.sin(a)
        px = x + ca * r
        py = y + sa * r
        if _solid_world(grid, px, py):
            nx_acc -= ca
            ny_acc -= sa
    if _solid_world(grid, x, y):
        gx = 0.0
        gy = 0.0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if not _solid_world(grid, x + float(dx), y + float(dy)):
                    gx += float(dx)
                    gy += float(dy)
        glen = math.hypot(gx, gy)
        if glen > 1e-6:
            return gx / glen, gy / glen
    slen = math.hypot(nx_acc, ny_acc)
    if slen < 1e-6:
        return 1.0, 0.0
    return nx_acc / slen, ny_acc / slen


def collide_ball_bitmap(
    x: float,
    y: float,
    vx: float,
    vy: float,
    r: float,
    grid: CollisionGrid,
    iterations: int = 4,
    rim_samples: int = 16,
    max_separate_steps: int = 96,
) -> tuple[float, float, float, float]:
    """
    Colisão círculo vs pixels sólidos (preto no mapa). Branco = livre.
    Iterações externas reduzem tuneling; separação interna passo-a-passo.
    """
    for _ in range(iterations):
        if not _circle_overlaps_bitmap(grid, x, y, r, rim_samples):
            break
        nx, ny = _escape_normal_bitmap(grid, x, y, r, rim_samples)
        vn = vx * nx + vy * ny
        if vn < 0:
            vx -= (1.0 + RESTITUTION) * vn * nx
            vy -= (1.0 + RESTITUTION) * vn * ny
        for _s in range(max_separate_steps):
            if not _circle_overlaps_bitmap(grid, x, y, r, rim_samples):
                break
            x += nx * 1.0
            y += ny * 1.0
            nx, ny = _escape_normal_bitmap(grid, x, y, r, rim_samples)
    return x, y, vx, vy


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
