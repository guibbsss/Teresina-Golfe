"""Tela de introdução: gradiente quente, silhuetas, partículas, CTA piscando."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass

import pygame

from tour_teresina_golf.config import (
    COLOR_UI_ACCENT,
    INTRO_SUB_COLOR,
    INTRO_TITLE_COLOR,
    LOGICAL_H,
    LOGICAL_W,
)


def make_vertical_gradient(size: tuple[int, int], top: tuple[int, int, int], bottom: tuple[int, int, int]) -> pygame.Surface:
    w, h = size
    surf = pygame.Surface(size)
    for y in range(h):
        t = y / max(h - 1, 1)
        r = int(top[0] * (1 - t) + bottom[0] * t)
        g = int(top[1] * (1 - t) + bottom[1] * t)
        b = int(top[2] * (1 - t) + bottom[2] * t)
        pygame.draw.line(surf, (r, g, b), (0, y), (w, y))
    return surf


@dataclass
class DustParticle:
    x: float
    y: float
    vy: float
    r: int
    a: int


class IntroState:
    def __init__(self) -> None:
        self.t0 = pygame.time.get_ticks()
        self.gradient = make_vertical_gradient((LOGICAL_W, LOGICAL_H), (255, 190, 120), (110, 72, 48))
        self.particles: list[DustParticle] = []
        for _ in range(44):
            self.particles.append(
                DustParticle(
                    x=random.uniform(0, LOGICAL_W),
                    y=random.uniform(0, LOGICAL_H),
                    vy=random.uniform(8, 38),
                    r=random.randint(1, 3),
                    a=random.randint(40, 110),
                )
            )

    def update(self) -> None:
        for p in self.particles:
            p.y -= p.vy * 0.016
            if p.y < -8:
                p.y = LOGICAL_H + random.uniform(0, 40)
                p.x = random.uniform(0, LOGICAL_W)

    def draw(self, screen: pygame.Surface, font_title: pygame.font.Font, font_sub: pygame.font.Font, font_ui: pygame.font.Font) -> None:
        screen.blit(self.gradient, (0, 0))
        t = (pygame.time.get_ticks() - self.t0) / 1000.0

        # Silhuetas urbanas simples (parallax leve)
        horizon = LOGICAL_H - 130
        pygame.draw.rect(screen, (55, 42, 48), (40 + math.sin(t * 0.35) * 6, horizon - 120, 70, 120))
        pygame.draw.rect(screen, (62, 48, 52), (200, horizon - 160, 95, 160))
        pygame.draw.rect(screen, (48, 62, 72), (420 + math.sin(t * 0.28 + 1) * 8, horizon - 95, 110, 95))
        pygame.draw.polygon(screen, (72, 92, 62), [(610, horizon), (670, horizon - 55), (730, horizon)])

        # Ruas / faixa horizonte
        pygame.draw.rect(screen, (52, 46, 44), (0, horizon, LOGICAL_W, LOGICAL_H - horizon))

        for p in self.particles:
            s = pygame.Surface((p.r * 2, p.r * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (255, 230, 180, p.a), (p.r, p.r), p.r)
            screen.blit(s, (int(p.x), int(p.y)))

        pulse = 1.0 + 0.04 * math.sin(t * 2.6)
        title_surf = font_title.render("Tour Teresina Golf", True, INTRO_TITLE_COLOR)
        tw, th = title_surf.get_size()
        scaled = pygame.transform.smoothscale(title_surf, (int(tw * pulse), int(th * pulse)))
        screen.blit(scaled, scaled.get_rect(center=(LOGICAL_W // 2, LOGICAL_H // 2 - 40)))

        sub_a = min(255, max(0, int(255 * min(1.0, (t - 0.25) * 2.0))))
        sub = font_sub.render("Mini golfe pelos cartões-postais de Teresina", True, INTRO_SUB_COLOR)
        sub.set_alpha(sub_a)
        screen.blit(sub, sub.get_rect(center=(LOGICAL_W // 2, LOGICAL_H // 2 + 18)))

        blink = 0.55 + 0.45 * math.sin(t * 3.2)
        cta = font_ui.render("Clique ou Enter para continuar", True, COLOR_UI_ACCENT)
        cta.set_alpha(int(255 * blink))
        screen.blit(cta, cta.get_rect(center=(LOGICAL_W // 2, LOGICAL_H - 72)))
