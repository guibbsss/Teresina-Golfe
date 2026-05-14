from __future__ import annotations
from enum import Enum, auto
import math
from pathlib import Path
import pygame
from tour_teresina_golf.config import SCREEN_HEIGHT, SCREEN_WIDTH
from tour_teresina_golf.draw_play import blit_ball_skin_preview
from tour_teresina_golf.resource_path import asset
from tour_teresina_golf.save_data import SaveData
MENU_BTN_FILL = (26, 67, 20)
MENU_BTN_BORDER = (78, 154, 49)
MENU_BTN_TEXT = (255, 248, 240)
MENU_ICON_PLAY = (255, 220, 60)
MENU_ICON_GEAR = (200, 210, 200)
MENU_ICON_TROPHY = (230, 190, 80)
MENU_ICON_DOOR = (120, 82, 55)
MENU_ICON_COIN = (255, 214, 80)
MENU_ICON_INFO = (240, 240, 240)
MENU_SHOP_BUTTON_ENABLED: bool = True

class MenuPanel(Enum):
    MAIN = auto()
    SETTINGS = auto()
    RANKING = auto()
    SHOP = auto()
    CREDITS = auto()

class MenuIcon(Enum):
    PLAY = auto()
    GEAR = auto()
    TROPHY = auto()
    COIN = auto()
    DOOR = auto()

def main_menu_button_count() -> int:
    return 5 if MENU_SHOP_BUTTON_ENABLED else 4

def main_menu_labels_and_icons() -> tuple[tuple[str, ...], tuple[MenuIcon, ...]]:
    if MENU_SHOP_BUTTON_ENABLED:
        return (('JOGAR', 'CONFIGURACOES', 'RANKING', 'LOJA', 'SAIR'), (MenuIcon.PLAY, MenuIcon.GEAR, MenuIcon.TROPHY, MenuIcon.COIN, MenuIcon.DOOR))
    return (('JOGAR', 'CONFIGURACOES', 'RANKING', 'SAIR'), (MenuIcon.PLAY, MenuIcon.GEAR, MenuIcon.TROPHY, MenuIcon.DOOR))
_FONT_PATH = asset('tour_teresina_golf/assets/fonts/PressStart2P-Regular.ttf')
_INTRO_MENUS_PATH = asset('Menus/intro.png')
_BG_PATH = asset('tour_teresina_golf/assets/menu_background.png')

def _button_rect(center_x: int, center_y: int, w: int, h: int) -> pygame.Rect:
    return pygame.Rect(0, 0, w, h).move(center_x - w // 2, center_y - h // 2)

def load_menu_pixel_fonts() -> tuple[pygame.font.Font, pygame.font.Font, pygame.font.Font]:
    pygame.font.init()
    if _FONT_PATH.is_file():
        return (pygame.font.Font(str(_FONT_PATH), 18), pygame.font.Font(str(_FONT_PATH), 14), pygame.font.Font(str(_FONT_PATH), 12))
    f18 = pygame.font.SysFont('consolas', 18, bold=True)
    f14 = pygame.font.SysFont('consolas', 14)
    f12 = pygame.font.SysFont('consolas', 12)
    return (f18, f14, f12)

def _load_scaled_png(path: Path) -> pygame.Surface:
    img = pygame.image.load(str(path)).convert()
    if img.get_size() != (SCREEN_WIDTH, SCREEN_HEIGHT):
        img = pygame.transform.smoothscale(img, (SCREEN_WIDTH, SCREEN_HEIGHT))
    return img

def load_menu_background_surface() -> tuple[pygame.Surface, bool]:
    if _INTRO_MENUS_PATH.is_file():
        return (_load_scaled_png(_INTRO_MENUS_PATH), True)
    if _BG_PATH.is_file():
        return (_load_scaled_png(_BG_PATH), True)
    return (_render_fallback_menu_background(), False)

def _render_fallback_menu_background() -> pygame.Surface:
    s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    for y in range(SCREEN_HEIGHT):
        t = y / max(1, SCREEN_HEIGHT - 1)
        r = int(80 + (135 - 80) * t)
        g = int(170 + (205 - 170) * t)
        b = int(235 + (255 - 235) * t)
        pygame.draw.line(s, (r, g, b), (0, y), (SCREEN_WIDTH, y))
    for cx, cy in ((120, 55), (420, 40), (700, 65)):
        for dx, dy, rad in ((0, 0, 28), (22, -5, 22), (-20, 4, 20)):
            pygame.draw.circle(s, (255, 255, 255), (cx + dx, cy + dy), rad)
    horizon = 310
    pygame.draw.ellipse(s, (42, 110, 62), (-80, SCREEN_HEIGHT - 140, SCREEN_WIDTH + 160, 200))
    pygame.draw.ellipse(s, (52, 130, 78), (40, SCREEN_HEIGHT - 128, SCREEN_WIDTH - 80, 160))
    pygame.draw.rect(s, (55, 52, 58), (0, horizon, SCREEN_WIDTH, SCREEN_HEIGHT - horizon))
    for x, w, h in ((40, 55, 120), (110, 70, 150), (200, 48, 95), (280, 60, 130), (360, 52, 110), (480, 75, 175), (600, 45, 100), (680, 58, 140)):
        pygame.draw.rect(s, (72, 62, 68), (x, horizon - h, w, h))
        pygame.draw.rect(s, (58, 50, 55), (x + 6, horizon - h + 20, w - 12, h - 20))
    bx = SCREEN_WIDTH - 120
    pygame.draw.line(s, (220, 220, 230), (bx, horizon - 20), (bx + 40, horizon - 140), 6)
    pygame.draw.line(s, (200, 200, 215), (bx, horizon - 20), (bx - 50, horizon - 90), 4)
    pygame.draw.line(s, (180, 190, 210), (bx - 50, horizon - 10), (bx + 80, horizon - 10), 5)
    pygame.draw.circle(s, (30, 32, 36), (SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT - 42), 14)
    pygame.draw.circle(s, (245, 245, 245), (SCREEN_WIDTH // 2 - 188, SCREEN_HEIGHT - 48), 8)
    return s

def _main_menu_stack_vertical_centers() -> tuple[float, int]:
    BTN_H = 42
    MARGIN_B = 22
    GAP = 8
    step = BTN_H + GAP
    y_bottom_center = SCREEN_HEIGHT - MARGIN_B - BTN_H // 2
    return (float(y_bottom_center), step)

def compute_main_menu_button_rects() -> list[pygame.Rect]:
    BTN_W, BTN_H = (282, 42)
    MARGIN_R = 24
    n = main_menu_button_count()
    y_bottom_center, step = _main_menu_stack_vertical_centers()
    cx = SCREEN_WIDTH - MARGIN_R - BTN_W // 2
    rects: list[pygame.Rect] = []
    for idx in range(n):
        j_from_bottom = n - 1 - idx
        cy = int(y_bottom_center - j_from_bottom * step)
        rects.append(pygame.Rect(cx - BTN_W // 2, cy - BTN_H // 2, BTN_W, BTN_H))
    return rects

def compute_settings_panel_rects() -> tuple[pygame.Rect, pygame.Rect]:
    PANEL_W = 340
    cx = SCREEN_WIDTH // 2
    h_fs, h_back = (46, 46)
    y_bottom_center, step = _main_menu_stack_vertical_centers()
    cy_back = int(y_bottom_center - 0 * step)
    cy_fs = int(y_bottom_center - 1 * step)
    opt_toggle_fs = _button_rect(cx, cy_fs, PANEL_W, h_fs)
    opt_back = _button_rect(cx, cy_back, 260, h_back)
    return (opt_toggle_fs, opt_back)

def compute_ranking_panel_rects() -> tuple[pygame.Rect, pygame.Rect]:
    panel_w = min(940, SCREEN_WIDTH - 20)
    panel_h = 280
    box = pygame.Rect(SCREEN_WIDTH // 2 - panel_w // 2, SCREEN_HEIGHT // 2 - 140, panel_w, panel_h)
    back = _button_rect(SCREEN_WIDTH // 2, box.bottom + 18, 200, 44)
    return (box, back)

def compute_credits_panel_rects() -> tuple[pygame.Rect, pygame.Rect]:
    panel_w = 820
    panel_h = 360
    box = pygame.Rect(SCREEN_WIDTH // 2 - panel_w // 2, SCREEN_HEIGHT // 2 - panel_h // 2, panel_w, panel_h)
    back = _button_rect(SCREEN_WIDTH // 2, box.bottom + 20, 200, 44)
    return (box, back)

def compute_menu_credits_chip_rect() -> pygame.Rect:
    w, h = (40, 30)
    margin_r, margin_t = (12, 12)
    return pygame.Rect(SCREEN_WIDTH - margin_r - w, margin_t, w, h)

def compute_shop_panel_rects(catalog: list[tuple[str, str, int]]) -> tuple[pygame.Rect, list[pygame.Rect], pygame.Rect]:
    box_w, box_h = (700, 300)
    box = pygame.Rect(SCREEN_WIDTH // 2 - box_w // 2, SCREEN_HEIGHT // 2 - box_h // 2, box_w, box_h)
    paid = catalog[1:]
    item_rects: list[pygame.Rect] = []
    row_h = 58
    row0_y = box.top + 78
    btn_w, btn_h = (200, 40)
    margin_r = 20
    for i in range(len(paid)):
        cy = row0_y + i * row_h + row_h // 2
        r = pygame.Rect(0, 0, btn_w, btn_h).move(box.right - margin_r - btn_w, cy - btn_h // 2)
        item_rects.append(r)
    back = _button_rect(SCREEN_WIDTH // 2, box.bottom + 20, 200, 44)
    return (box, item_rects, back)

def _draw_icon_play(surf: pygame.Surface, cx: int, cy: int, size: int=12) -> None:
    pts = [(cx - size // 2, cy - size // 2), (cx - size // 2, cy + size // 2), (cx + size // 2, cy)]
    pygame.draw.polygon(surf, MENU_ICON_PLAY, pts)

def _draw_icon_gear(surf: pygame.Surface, cx: int, cy: int) -> None:
    r = 10
    pygame.draw.circle(surf, MENU_ICON_GEAR, (cx, cy), r, 2)
    for i in range(8):
        ang = i * math.pi / 4
        x1 = cx + math.cos(ang) * (r - 2)
        y1 = cy + math.sin(ang) * (r - 2)
        x2 = cx + math.cos(ang) * (r + 5)
        y2 = cy + math.sin(ang) * (r + 5)
        pygame.draw.line(surf, MENU_ICON_GEAR, (x1, y1), (x2, y2), 2)

def _draw_icon_trophy(surf: pygame.Surface, cx: int, cy: int) -> None:
    pygame.draw.polygon(surf, MENU_ICON_TROPHY, [(cx, cy - 10), (cx - 9, cy + 6), (cx + 9, cy + 6)])
    pygame.draw.rect(surf, MENU_ICON_TROPHY, (cx - 10, cy + 6, 20, 5))
    pygame.draw.rect(surf, MENU_ICON_TROPHY, (cx - 6, cy + 10, 12, 4))

def _draw_icon_door(surf: pygame.Surface, cx: int, cy: int) -> None:
    pygame.draw.rect(surf, MENU_ICON_DOOR, (cx - 9, cy - 10, 18, 22), border_radius=2)
    pygame.draw.circle(surf, (220, 200, 120), (cx + 4, cy), 2)
    pygame.draw.polygon(surf, (120, 200, 100), [(cx - 4, cy - 3), (cx - 4, cy + 3), (cx + 4, cy)])

def _draw_icon_coin(surf: pygame.Surface, cx: int, cy: int) -> None:
    pygame.draw.circle(surf, MENU_ICON_COIN, (cx, cy), 10)
    pygame.draw.circle(surf, (200, 160, 40), (cx, cy), 10, width=2)
    pygame.draw.arc(surf, (40, 30, 20), (cx - 6, cy - 6, 12, 12), 0.9, 2.6, 2)

def _draw_icon_info(surf: pygame.Surface, cx: int, cy: int) -> None:
    pygame.draw.circle(surf, MENU_ICON_INFO, (cx, cy), 10, width=2)
    pygame.draw.rect(surf, MENU_ICON_INFO, (cx - 1, cy - 5, 3, 3))
    pygame.draw.rect(surf, MENU_ICON_INFO, (cx - 1, cy - 1, 3, 7))

def _draw_menu_icon(surf: pygame.Surface, kind: MenuIcon, cx: int, cy: int) -> None:
    if kind == MenuIcon.PLAY:
        _draw_icon_play(surf, cx, cy)
    elif kind == MenuIcon.GEAR:
        _draw_icon_gear(surf, cx, cy)
    elif kind == MenuIcon.TROPHY:
        _draw_icon_trophy(surf, cx, cy)
    elif kind == MenuIcon.COIN:
        _draw_icon_coin(surf, cx, cy)
    else:
        _draw_icon_door(surf, cx, cy)

def draw_menu_credits_chip(surf: pygame.Surface, rect: pygame.Rect) -> None:
    pygame.draw.rect(surf, MENU_BTN_FILL, rect, border_radius=6)
    pygame.draw.rect(surf, MENU_BTN_BORDER, rect, width=2, border_radius=6)
    _draw_icon_info(surf, rect.centerx, rect.centery)

def draw_main_menu_buttons(surf: pygame.Surface, font_label: pygame.font.Font, rects: list[pygame.Rect], labels: tuple[str, ...], icons: tuple[MenuIcon, ...]) -> None:
    for rect, label, icon in zip(rects, labels, icons):
        pygame.draw.rect(surf, MENU_BTN_FILL, rect, border_radius=8)
        pygame.draw.rect(surf, MENU_BTN_BORDER, rect, width=2, border_radius=8)
        icx = rect.left + 26
        icy = rect.centery
        _draw_menu_icon(surf, icon, icx, icy)
        tx = font_label.render(label, True, MENU_BTN_TEXT)
        surf.blit(tx, tx.get_rect(midleft=(rect.left + 48, rect.centery)))

def draw_menu_background(surf: pygame.Surface, bg: pygame.Surface) -> None:
    surf.blit(bg, (0, 0))

def draw_settings_overlay(surf: pygame.Surface, font_ui: pygame.font.Font, font_small: pygame.font.Font, settings: object, rects: tuple[pygame.Rect, pygame.Rect]) -> None:
    opt_toggle_fs_rect, opt_back_rect = rects
    fs = getattr(settings, 'fullscreen')
    fs_label = 'Ecra inteiro: ligado' if fs else 'Ecra inteiro: desligado'
    pygame.draw.rect(surf, MENU_BTN_FILL, opt_toggle_fs_rect, border_radius=8)
    pygame.draw.rect(surf, MENU_BTN_BORDER, opt_toggle_fs_rect, width=2, border_radius=8)
    t_fs = font_ui.render(fs_label, True, MENU_BTN_TEXT)
    surf.blit(t_fs, t_fs.get_rect(center=opt_toggle_fs_rect.center))
    pygame.draw.rect(surf, MENU_BTN_FILL, opt_back_rect, border_radius=8)
    pygame.draw.rect(surf, MENU_BTN_BORDER, opt_back_rect, width=2, border_radius=8)
    t_back = font_small.render('VOLTAR', True, MENU_BTN_TEXT)
    surf.blit(t_back, t_back.get_rect(center=opt_back_rect.center))

def _five_point_star_points(cx: float, cy: float, outer: float) -> list[tuple[int, int]]:
    inner = outer * 0.42
    pts: list[tuple[int, int]] = []
    for i in range(10):
        ang = -math.pi / 2 + i * (math.pi / 5)
        rad = outer if i % 2 == 0 else inner
        pts.append((int(cx + math.cos(ang) * rad), int(cy + math.sin(ang) * rad)))
    return pts

def _fit_label_surface(font: pygame.font.Font, text: str, max_width: int, color: tuple[int, int, int]) -> pygame.Surface:
    surf = font.render(text, True, color)
    if surf.get_width() <= max_width:
        return surf
    ell = '...'
    t = text
    while len(t) > 0:
        surf = font.render(t + ell, True, color)
        if surf.get_width() <= max_width:
            return surf
        t = t[:-1]
    return font.render(ell, True, color)

def draw_ranking_overlay(surf: pygame.Surface, font_title: pygame.font.Font, font_ui: pygame.font.Font, box_rect: pygame.Rect, back_rect: pygame.Rect, save_data: SaveData) -> None:
    veil = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    veil.fill((10, 14, 18, 145))
    surf.blit(veil, (0, 0))
    pygame.draw.rect(surf, (22, 38, 22), box_rect, border_radius=14)
    pygame.draw.rect(surf, MENU_BTN_BORDER, box_rect, width=3, border_radius=14)
    t = font_title.render('RANKING', True, MENU_BTN_TEXT)
    surf.blit(t, t.get_rect(midtop=(box_rect.centerx, box_rect.top + 18)))
    phase_info = (('fase1', 'Avenida Frei Serafim'), ('fase2', 'Ponte Estaiada'), ('fase3', 'Encontro dos Rios'))
    gold = (255, 214, 80)
    dim = (100, 90, 60)
    text_c = (220, 215, 200)
    muted = (160, 150, 130)
    row_y = box_rect.top + 54
    row_h = 58
    left_pad = 14
    right_pad = 12
    r_col_w = 176
    after_label_gap = 22
    result_col_left_max = box_rect.right - right_pad - r_col_w
    label_x = box_rect.left + left_pad
    max_label_w = max(160, result_col_left_max - label_x - after_label_gap)
    for pid, label in phase_info:
        rec = getattr(save_data, pid, None)
        stars_val = rec.stars if rec is not None else 0
        strokes_used = rec.strokes_used if rec is not None else 999
        full = f'Fase {label}'
        t_label = _fit_label_surface(font_ui, full, max_label_w, text_c)
        surf.blit(t_label, (label_x, row_y + (row_h - t_label.get_height()) // 2))
        label_right = label_x + t_label.get_width()
        stars_zone_left = min(label_right + after_label_gap, result_col_left_max)
        zone_cx = stars_zone_left + r_col_w // 2
        row_cy = row_y + row_h // 2
        if stars_val == 0:
            t_none = font_ui.render('Nao jogada', True, muted)
            surf.blit(t_none, t_none.get_rect(center=(zone_cx, row_cy)))
        else:
            outer = max(6, font_ui.get_height() // 3)
            pitch = max(3, outer // 3)
            slot = 2 * outer + pitch
            total_sw = 3 * slot - pitch
            sx0 = zone_cx - total_sw // 2 + outer
            cy_s = row_cy - 8
            for i in range(3):
                filled = i < stars_val
                cx_s = sx0 + i * slot
                pts = _five_point_star_points(float(cx_s), float(cy_s), float(outer))
                w_line = max(1, outer // 5)
                if filled:
                    pygame.draw.polygon(surf, gold, pts)
                else:
                    pygame.draw.polygon(surf, dim, pts, width=w_line)
            if strokes_used < 900:
                t_st = font_ui.render(f'{strokes_used} tacadas', True, muted)
                surf.blit(t_st, t_st.get_rect(midtop=(zone_cx, cy_s + outer + 8)))
        row_y += row_h
    pygame.draw.rect(surf, MENU_BTN_FILL, back_rect, border_radius=8)
    pygame.draw.rect(surf, MENU_BTN_BORDER, back_rect, width=2, border_radius=8)
    vb = font_ui.render('VOLTAR', True, MENU_BTN_TEXT)
    surf.blit(vb, vb.get_rect(center=back_rect.center))

def draw_credits_overlay(surf: pygame.Surface, font_title: pygame.font.Font, font_ui: pygame.font.Font, font_small: pygame.font.Font, box_rect: pygame.Rect, back_rect: pygame.Rect) -> None:
    veil = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    veil.fill((10, 14, 18, 145))
    surf.blit(veil, (0, 0))
    pygame.draw.rect(surf, (22, 38, 22), box_rect, border_radius=14)
    pygame.draw.rect(surf, MENU_BTN_BORDER, box_rect, width=3, border_radius=14)
    t_head = font_title.render('CREDITOS', True, MENU_BTN_TEXT)
    surf.blit(t_head, t_head.get_rect(midtop=(box_rect.centerx, box_rect.top + 18)))
    t_sub = font_ui.render('Tour Teresina Golf', True, (255, 214, 80))
    surf.blit(t_sub, t_sub.get_rect(midtop=(box_rect.centerx, box_rect.top + 38)))
    sep_y1 = box_rect.top + 54
    pygame.draw.line(surf, MENU_BTN_BORDER, (box_rect.left + 12, sep_y1), (box_rect.right - 12, sep_y1), 1)
    max_text_w = box_rect.width - 60
    g1 = 'Gabriel Lages Oliveira de Azevedo'
    g2 = 'Guilherme Ruben Pereira Matos'
    f_g1 = font_small if font_ui.size(g1)[0] > max_text_w else font_ui
    f_g2 = font_small if font_ui.size(g2)[0] > max_text_w else font_ui
    y_tech = box_rect.top + 174
    c_sec = (180, 200, 160)
    c_name = (240, 240, 220)
    c_role = (160, 180, 140)
    c_tech = (200, 210, 195)
    lx = box_rect.left
    t_eq = font_ui.render('EQUIPE', True, c_sec)
    surf.blit(t_eq, (lx + 20, box_rect.top + 60))
    s1 = f_g1.render(g1, True, c_name)
    surf.blit(s1, (lx + 28, box_rect.top + 82))
    r1 = font_small.render('Programacao e Fisica', True, c_role)
    surf.blit(r1, (lx + 38, box_rect.top + 100))
    s2 = f_g2.render(g2, True, c_name)
    surf.blit(s2, (lx + 28, box_rect.top + 124))
    r2 = font_small.render('Assets e Level Design', True, c_role)
    surf.blit(r2, (lx + 38, box_rect.top + 142))
    sep_y2 = y_tech - 12
    pygame.draw.line(surf, MENU_BTN_BORDER, (box_rect.left + 12, sep_y2), (box_rect.right - 12, sep_y2), 1)
    t_tec = font_ui.render('TECNOLOGIA', True, c_sec)
    surf.blit(t_tec, (lx + 20, y_tech))
    t_py = font_small.render('Python 3 + Pygame', True, c_tech)
    surf.blit(t_py, (lx + 38, box_rect.top + 196))
    t_cur = font_ui.render('CURSO', True, c_sec)
    surf.blit(t_cur, (lx + 20, box_rect.top + 224))
    t_turma = font_small.render('Turma Zeta  -  7 Periodo  -  ICEV', True, c_tech)
    surf.blit(t_turma, (lx + 38, box_rect.top + 246))
    pygame.draw.rect(surf, MENU_BTN_FILL, back_rect, border_radius=8)
    pygame.draw.rect(surf, MENU_BTN_BORDER, back_rect, width=2, border_radius=8)
    vb = font_small.render('VOLTAR', True, MENU_BTN_TEXT)
    surf.blit(vb, vb.get_rect(center=back_rect.center))

def draw_shop_overlay(surf: pygame.Surface, font_title: pygame.font.Font, font_ui: pygame.font.Font, font_small: pygame.font.Font, box_rect: pygame.Rect, item_rects: list[pygame.Rect], back_rect: pygame.Rect, catalog: list[tuple[str, str, int]], save_data: SaveData) -> None:
    veil = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    veil.fill((10, 14, 18, 145))
    surf.blit(veil, (0, 0))
    pygame.draw.rect(surf, (22, 38, 22), box_rect, border_radius=14)
    pygame.draw.rect(surf, MENU_BTN_BORDER, box_rect, width=3, border_radius=14)
    t = font_title.render('LOJA', True, MENU_BTN_TEXT)
    surf.blit(t, t.get_rect(midtop=(box_rect.centerx, box_rect.top + 14)))
    bal = font_ui.render(f'Caju Coins: {save_data.caju_coins}', True, (255, 214, 80))
    surf.blit(bal, bal.get_rect(midtop=(box_rect.centerx, box_rect.top + 44)))
    paid = catalog[1:]
    preview = pygame.Rect(0, 0, 24, 24)
    row_h = 58
    row0_y = box_rect.top + 78
    left_x = box_rect.left + 18
    text_c = (220, 215, 200)
    muted = (120, 115, 105)
    for i, (skin_id, disp_name, cost) in enumerate(paid):
        row_cy = row0_y + i * row_h + row_h // 2
        preview.center = (left_x + 12, row_cy)
        blit_ball_skin_preview(surf, preview, skin_id)
        name_s = font_ui.render(disp_name, True, text_c)
        surf.blit(name_s, (left_x + 32, row_cy - name_s.get_height() // 2))
        btn = item_rects[i]
        unlocked = skin_id in save_data.unlocked_skins
        active = save_data.active_skin == skin_id
        can_buy = save_data.caju_coins >= cost
        if unlocked and active:
            label = 'Equipada'
            fill = (55, 62, 55)
            border = (100, 110, 95)
            tc = muted
        elif unlocked:
            label = 'Equipar'
            fill = MENU_BTN_FILL
            border = MENU_BTN_BORDER
            tc = MENU_BTN_TEXT
        elif can_buy:
            label = f'Comprar ({cost})'
            fill = MENU_BTN_FILL
            border = MENU_BTN_BORDER
            tc = MENU_BTN_TEXT
        else:
            label = f'Comprar ({cost})'
            fill = (48, 48, 52)
            border = (72, 72, 78)
            tc = muted
        pygame.draw.rect(surf, fill, btn, border_radius=8)
        pygame.draw.rect(surf, border, btn, width=2, border_radius=8)
        tb = font_small.render(label, True, tc)
        surf.blit(tb, tb.get_rect(center=btn.center))
    pygame.draw.rect(surf, MENU_BTN_FILL, back_rect, border_radius=8)
    pygame.draw.rect(surf, MENU_BTN_BORDER, back_rect, width=2, border_radius=8)
    vb = font_ui.render('VOLTAR', True, MENU_BTN_TEXT)
    surf.blit(vb, vb.get_rect(center=back_rect.center))
