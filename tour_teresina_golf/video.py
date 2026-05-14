from __future__ import annotations
import pygame
from tour_teresina_golf.config import LOGICAL_H, LOGICAL_W
from tour_teresina_golf.settings import UserSettings

_CHROME_MARGIN_X = 48
_CHROME_MARGIN_Y = 96


def _max_safe_window_scale() -> int:
    """Maior escala inteira em que LOGICAL_W/H * escala cabe na área útil do monitor principal."""
    dw = dh = 0
    try:
        sizes = pygame.display.get_desktop_sizes()
        if sizes:
            dw, dh = int(sizes[0][0]), int(sizes[0][1])
    except (AttributeError, TypeError, ValueError, pygame.error):
        pass
    if dw < LOGICAL_W or dh < LOGICAL_H:
        try:
            info = pygame.display.Info()
            dw = max(dw, int(info.current_w))
            dh = max(dh, int(info.current_h))
        except (AttributeError, TypeError, ValueError, pygame.error):
            pass
    if dw < LOGICAL_W or dh < LOGICAL_H:
        return 6
    avail_w = max(LOGICAL_W, dw - _CHROME_MARGIN_X)
    avail_h = max(LOGICAL_H, dh - _CHROME_MARGIN_Y)
    max_sw = avail_w // LOGICAL_W
    max_sh = avail_h // LOGICAL_H
    return max(1, min(6, min(max_sw, max_sh)))


class DisplayPresenter:

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
            sx = dw / float(LOGICAL_W)
            sy = dh / float(LOGICAL_H)
            self._present_scale = min(sx, sy)
            self._letter_offset_x = 0
            self._letter_offset_y = 0

    def apply_video_mode(self, s: UserSettings) -> pygame.Surface:
        self.configure_from_settings(s)
        if s.fullscreen:
            screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            max_s = _max_safe_window_scale()
            if self._window_scale > max_s:
                self._window_scale = max_s
                s.window_scale = max_s
                s.clamp()
            w = LOGICAL_W * self._window_scale
            h = LOGICAL_H * self._window_scale
            screen = pygame.display.set_mode((w, h))
        self.update_after_flip()
        return screen

    def window_to_logical(self, pos: tuple[int, int]) -> tuple[float, float]:
        mx, my = (float(pos[0]), float(pos[1]))
        if self._fullscreen:
            lx = (mx - self._letter_offset_x) / self._present_scale
            ly = (my - self._letter_offset_y) / self._present_scale
        else:
            lx = mx / self._present_scale
            ly = my / self._present_scale
        lx = max(0.0, min(float(LOGICAL_W - 1), lx))
        ly = max(0.0, min(float(LOGICAL_H - 1), ly))
        return (lx, ly)

    def present(self, logical: pygame.Surface, physical: pygame.Surface) -> None:
        dw, dh = physical.get_size()
        if self._fullscreen:
            sw = int(LOGICAL_W * self._present_scale)
            sh = int(LOGICAL_H * self._present_scale)
            scaled = pygame.transform.scale(logical, (sw, sh))
            physical.fill((0, 0, 0))
            physical.blit(scaled, (self._letter_offset_x, self._letter_offset_y))
        else:
            scaled = pygame.transform.scale(logical, (dw, dh))
            physical.blit(scaled, (0, 0))
