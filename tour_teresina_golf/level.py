"""Definição declarativa de fases (paredes AA, água, buraco, spawn)."""

from __future__ import annotations

from dataclasses import dataclass, field

import pygame


@dataclass
class Level:
    id: str
    name: str
    strokes: int
    ball_spawn: tuple[float, float]
    hole_center: tuple[float, float]
    walls: list[pygame.Rect] = field(default_factory=list)
    obstacles: list[pygame.Rect] = field(default_factory=list)
    water: list[pygame.Rect] = field(default_factory=list)
    play_rect: pygame.Rect | None = None


def build_rect_wall_ring(inner: pygame.Rect, thickness: int) -> list[pygame.Rect]:
    """Quatro paredes ao redor do retângulo interno jogável."""
    x, y, w, h = inner.x, inner.y, inner.w, inner.h
    t = thickness
    return [
        pygame.Rect(x - t, y - t, w + 2 * t, t),
        pygame.Rect(x - t, y + h, w + 2 * t, t),
        pygame.Rect(x - t, y, t, h),
        pygame.Rect(x + w, y, t, h),
    ]


def make_test_level() -> Level:
    """Arena de validação: corredor, canteiros, faixa de água lateral."""
    inner = pygame.Rect(80, 70, 800, 400)
    walls = build_rect_wall_ring(inner, 26)
    obstacles = [
        pygame.Rect(inner.x + 280, inner.y + 120, 72, 72),
        pygame.Rect(inner.x + 420, inner.y + 200, 90, 110),
    ]
    water = [
        pygame.Rect(inner.x + 24, inner.y + 260, 130, 52),
    ]
    return Level(
        id="test",
        name="Fase teste",
        strokes=10,
        ball_spawn=(inner.x + 55, inner.y + inner.h // 2),
        hole_center=(inner.right - 95, inner.y + inner.h // 2),
        walls=walls,
        obstacles=obstacles,
        water=water,
        play_rect=inner,
    )
