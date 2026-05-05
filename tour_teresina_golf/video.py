"""Buffer lógico 960×540, escala para janela ou fullscreen com letterbox e conversão do rato."""

from __future__ import annotations

import pygame

from tour_teresina_golf.config import LOGICAL_H, LOGICAL_W
from tour_teresina_golf.settings import UserSettings


class DisplayPresenter:
    """Mantém flags de apresentação e mapeia coordenadas janela ↔ espaço lógico."""

    def __init__(self) -> None:
        self._fullscreen = False
        self._window_scale = 2
        self._letter_offset_x = 0
        self._letter_offset_y = 0
        self._present_scale = 1.0

    def configure_from_settings(self, s: UserSettings) -> None:
        self._fullscreen = s.fullscreen
        self._window_scale = max(1, min(6, s.window_scale))

    def update_after_flip(self) -> None:
        """Recalcula letterbox após set_mode (fullscreen pode mudar tamanho real)."""
        surf = pygame.display.get_surface()
        if surf is None:
            return
        dw, dh = surf.get_size()
        if self._fullscreen:
            scale_fit = min(dw / LOGICAL_W, dh / LOGICAL_H)
            self._present_scale = scale_fit
            sw = int(LOGICAL_W * scale_fit)
            sh = int(LOGICAL_H * scale_fit)
            self._letter_offset_x = (dw - sw) // 2
            self._letter_offset_y = (dh - sh) // 2
        else:
            self._present_scale = float(self._window_scale)
            self._letter_offset_x = 0
            self._letter_offset_y = 0

    def apply_video_mode(self, s: UserSettings) -> pygame.Surface:
        """Cria ou altera o modo de vídeo; devolve a superfície principal (tamanho físico)."""
        self.configure_from_settings(s)
        if s.fullscreen:
            screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            w = LOGICAL_W * self._window_scale
            h = LOGICAL_H * self._window_scale
            screen = pygame.display.set_mode((w, h))
        self.update_after_flip()
        return screen

    def window_to_logical(self, pos: tuple[int, int]) -> tuple[float, float]:
        mx, my = float(pos[0]), float(pos[1])
        if self._fullscreen:
            lx = (mx - self._letter_offset_x) / self._present_scale
            ly = (my - self._letter_offset_y) / self._present_scale
        else:
            lx = mx / self._present_scale
            ly = my / self._present_scale
        lx = max(0.0, min(float(LOGICAL_W - 1), lx))
        ly = max(0.0, min(float(LOGICAL_H - 1), ly))
        return lx, ly

    def present(self, logical: pygame.Surface, physical: pygame.Surface) -> None:
        """Escala o buffer lógico para o rect central e copia para o ecrã."""
        dw, dh = physical.get_size()
        if self._fullscreen:
            # Mesmas dimensões que update_after_flip() (letterbox + window_to_logical).
            sw = int(LOGICAL_W * self._present_scale)
            sh = int(LOGICAL_H * self._present_scale)
            # scale (vizinho mais próximo) mantém texto/HUD legíveis; smoothscale borrava UI no fullscreen
            scaled = pygame.transform.scale(logical, (sw, sh))
            physical.fill((0, 0, 0))
            physical.blit(scaled, (self._letter_offset_x, self._letter_offset_y))
        else:
            scaled = pygame.transform.scale(logical, (dw, dh))
            physical.blit(scaled, (0, 0))
