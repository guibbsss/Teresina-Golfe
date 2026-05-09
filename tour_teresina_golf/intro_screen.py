"""Tela de introdução: imagem partilhada com o menu + convite para continuar."""

from __future__ import annotations

import math

import pygame

from tour_teresina_golf.config import COLOR_UI_ACCENT, LOGICAL_H, LOGICAL_W


class IntroState:
    """Usa a mesma superfície de fundo que o menu (carregada em ``app.run``)."""

    def __init__(self, background: pygame.Surface) -> None:
        self.background = background
        self.t0 = pygame.time.get_ticks()

    def update(self) -> None:
        pass

    def draw(self, screen: pygame.Surface, font_title: pygame.font.Font, font_sub: pygame.font.Font, font_ui: pygame.font.Font) -> None:
        del font_title, font_sub  # título/subtítulo estão na arte
        screen.blit(self.background, (0, 0))
        t = (pygame.time.get_ticks() - self.t0) / 1000.0
        blink = 0.55 + 0.45 * math.sin(t * 3.2)
        cta = font_ui.render("Clique ou Enter para continuar", True, COLOR_UI_ACCENT)
        cta.set_alpha(int(255 * blink))
        screen.blit(cta, cta.get_rect(center=(LOGICAL_W // 2, LOGICAL_H - 72)))
