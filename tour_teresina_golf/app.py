from __future__ import annotations
from enum import Enum, auto
from pathlib import Path
import pygame
from tour_teresina_golf import audio_stub
from tour_teresina_golf.config import FIXED_DT, LOGICAL_H, LOGICAL_W, PHYS_ACCUM_LIMIT, SCREEN_HEIGHT, SCREEN_WIDTH, SKIN_CATALOG, START_LEVEL_ID, TITLE
from tour_teresina_golf.draw_play import draw_aim, draw_ball, draw_hud, draw_pause_overlay, draw_playfield, draw_programmatic_hole_and_flag
from tour_teresina_golf.intro_screen import IntroState
from tour_teresina_golf.level import make_level_by_id
from tour_teresina_golf.main_menu_ui import MENU_SHOP_BUTTON_ENABLED, MenuPanel, compute_credits_panel_rects, compute_main_menu_button_rects, compute_menu_credits_chip_rect, compute_ranking_panel_rects, compute_settings_panel_rects, compute_shop_panel_rects, draw_credits_overlay, draw_main_menu_buttons, draw_menu_background, draw_menu_credits_chip, draw_ranking_overlay, draw_settings_overlay, draw_shop_overlay, load_menu_background_surface, load_menu_pixel_fonts, main_menu_labels_and_icons
from tour_teresina_golf.play_round import RoundOutcome, RoundSession, calc_stars
from tour_teresina_golf.save_data import award_coins, load_save_data, purchase_skin, save_save_data, set_active_skin, update_best_score
from tour_teresina_golf.settings import load_settings, save_settings
from tour_teresina_golf.video import DisplayPresenter
_REPO_ROOT = Path(__file__).resolve().parent.parent
_DEFEAT_LAYOUT_W = 1920
_DEFEAT_LAYOUT_H = 1080
_DEFEAT_BTN_MENU_LAYOUT = (400, 881)
_DEFEAT_BTN_RETRY_LAYOUT = (1250, 850)
_DEFEAT_BTN_GAP = 16

def _load_game_over_assets() -> tuple[pygame.Surface, pygame.Surface, pygame.Surface, pygame.Rect, pygame.Rect]:
    bg_native = pygame.image.load(str(_REPO_ROOT / 'telas' / 'Tela de Derrota.png')).convert()
    nw, nh = bg_native.get_size()
    bg = pygame.transform.smoothscale(bg_native, (LOGICAL_W, LOGICAL_H))
    lx = LOGICAL_W / float(_DEFEAT_LAYOUT_W)
    ly = LOGICAL_H / float(_DEFEAT_LAYOUT_H)
    menu_native = pygame.image.load(str(_REPO_ROOT / 'botoes' / 'Voltar_ao_Menu-removebg-preview.png')).convert_alpha()
    retry_native = pygame.image.load(str(_REPO_ROOT / 'botoes' / 'Reiniciar_Fase-removebg-preview.png')).convert_alpha()
    mw, mh = menu_native.get_size()
    bw0 = max(1, int(round(mw * lx)))
    bh0 = max(1, int(round(mh * ly)))
    mxl, myl = _DEFEAT_BTN_MENU_LAYOUT
    rxl, ryl = _DEFEAT_BTN_RETRY_LAYOUT
    mx = int(round(mxl * lx))
    my = int(round(myl * ly))
    rx = int(round(rxl * lx))
    ry = int(round(ryl * ly))
    gap = _DEFEAT_BTN_GAP
    shrink = 1.0
    if rx + bw0 > LOGICAL_W - gap:
        shrink = min(shrink, (LOGICAL_W - gap - rx) / float(bw0))
    if mx + bw0 > rx - gap:
        shrink = min(shrink, max(0.1, (rx - gap - mx) / float(bw0)))
    bw = max(1, int(round(bw0 * shrink)))
    bh = max(1, int(round(bh0 * shrink)))
    menu_s = pygame.transform.smoothscale(menu_native, (bw, bh))
    retry_s = pygame.transform.smoothscale(retry_native, (bw, bh))
    menu_rect = pygame.Rect(mx, my, bw, bh)
    retry_rect = pygame.Rect(rx, ry, bw, bh)
    margin = 8
    if retry_rect.right > LOGICAL_W - margin:
        retry_rect.x = LOGICAL_W - margin - retry_rect.w
    retry_rect.x = max(margin, retry_rect.x)
    menu_rect.x = LOGICAL_W - retry_rect.right
    menu_rect.x = max(margin, menu_rect.x)
    if menu_rect.right + gap > retry_rect.x:
        retry_rect.x = min(retry_rect.x, LOGICAL_W - margin - retry_rect.w)
        retry_rect.x = max(menu_rect.right + gap, retry_rect.x)
        if retry_rect.right > LOGICAL_W - margin:
            retry_rect.x = LOGICAL_W - margin - retry_rect.w
        menu_rect.x = max(margin, LOGICAL_W - retry_rect.right)
    bottom = min(LOGICAL_H - margin, max(my + bh, ry + bh))
    y_common = max(margin, bottom - bh)
    menu_rect.y = y_common
    retry_rect.y = y_common
    for r in (menu_rect, retry_rect):
        if r.bottom > LOGICAL_H - margin:
            dy = LOGICAL_H - margin - r.bottom
            menu_rect.y += dy
            retry_rect.y += dy
        if r.y < margin:
            dy = margin - r.y
            menu_rect.y += dy
            retry_rect.y += dy
    return (bg, menu_s, retry_s, menu_rect, retry_rect)
_VICTORY_CONTINUE_TO: dict[str, str] = {'fase1': 'fase2', 'fase2': 'fase3'}

def _layout_bottom_row_symmetric(natives: list[pygame.Surface]) -> tuple[list[pygame.Surface], list[pygame.Rect]]:
    lx = LOGICAL_W / float(_DEFEAT_LAYOUT_W)
    ly = LOGICAL_H / float(_DEFEAT_LAYOUT_H)
    gap = _DEFEAT_BTN_GAP
    margin = 8
    max_h = max((s.get_height() for s in natives))
    bh0 = max(1, int(round(max_h * ly)))
    scaled: list[pygame.Surface] = []
    for surf in natives:
        w, h = surf.get_size()
        bw = max(1, int(round(w * bh0 / float(h))))
        scaled.append(pygame.transform.smoothscale(surf, (bw, bh0)))
    widths = [s.get_width() for s in scaled]
    n = len(widths)
    total_w = sum(widths) + (n - 1) * gap
    avail = LOGICAL_W - 2 * margin
    if total_w > avail:
        f = avail / float(total_w)
        bh = max(1, int(round(bh0 * f)))
        scaled.clear()
        for surf in natives:
            w, h = surf.get_size()
            bw = max(1, int(round(w * bh / float(h))))
            scaled.append(pygame.transform.smoothscale(surf, (bw, bh)))
        widths = [s.get_width() for s in scaled]
        total_w = sum(widths) + (n - 1) * gap
    start_x = margin + max(0, (avail - total_w) // 2)
    y_bottom = LOGICAL_H - margin
    rects: list[pygame.Rect] = []
    x = start_x
    for s in scaled:
        rects.append(pygame.Rect(x, y_bottom - s.get_height(), s.get_width(), s.get_height()))
        x += s.get_width() + gap
    return (scaled, rects)

def _load_victory_assets_pack() -> tuple[pygame.Surface, pygame.Surface, pygame.Surface, pygame.Surface, pygame.Rect, pygame.Rect, pygame.Rect, pygame.Surface, pygame.Surface, pygame.Rect, pygame.Rect]:
    bg_native = pygame.image.load(str(_REPO_ROOT / 'telas' / 'Tela de vitória.png')).convert()
    bg = pygame.transform.smoothscale(bg_native, (LOGICAL_W, LOGICAL_H))
    next_n = pygame.image.load(str(_REPO_ROOT / 'botoes' / 'Proxima_Fase-removebg-preview.png')).convert_alpha()
    menu_n = pygame.image.load(str(_REPO_ROOT / 'botoes' / 'Voltar_ao_Menu-removebg-preview.png')).convert_alpha()
    retry_n = pygame.image.load(str(_REPO_ROOT / 'botoes' / 'Reiniciar_Fase-removebg-preview.png')).convert_alpha()
    s3, r3 = _layout_bottom_row_symmetric([next_n, menu_n, retry_n])
    s2, r2 = _layout_bottom_row_symmetric([menu_n, retry_n])
    return (bg, s3[0], s3[1], s3[2], r3[0], r3[1], r3[2], s2[0], s2[1], r2[0], r2[1])

class GameScreen(Enum):
    INTRO = auto()
    MENU = auto()
    PLAY = auto()
    VICTORY = auto()
    GAME_OVER = auto()
    PAUSED = auto()
    POST_GAME_CREDITS = auto()

def _make_fonts() -> tuple[pygame.font.Font, pygame.font.Font, pygame.font.Font, pygame.font.Font]:
    pygame.font.init()
    title = pygame.font.SysFont('consolas', 52, bold=True)
    sub = pygame.font.SysFont('consolas', 22)
    ui = pygame.font.SysFont('consolas', 20)
    ui_big = pygame.font.SysFont('consolas', 26)
    return (title, sub, ui, ui_big)

def _button_rect(center_x: int, center_y: int, w: int, h: int) -> pygame.Rect:
    return pygame.Rect(0, 0, w, h).move(center_x - w // 2, center_y - h // 2)

def _victory_fase3_credits_btn_rect() -> pygame.Rect:
    return pygame.Rect(SCREEN_WIDTH - 118, SCREEN_HEIGHT - 52, 108, 36)

def run() -> None:
    pygame.init()
    pygame.display.set_caption(TITLE)
    settings = load_settings()
    presenter = DisplayPresenter()
    physical_screen = presenter.apply_video_mode(settings)
    logical_screen = pygame.Surface((LOGICAL_W, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    font_title, font_sub, font_ui, font_ui_big = _make_fonts()
    menu_bg, _ = load_menu_background_surface()
    menu_font_title, menu_font_btn, menu_font_hint = load_menu_pixel_fonts()
    menu_panel = MenuPanel.MAIN
    menu_btn_rects = compute_main_menu_button_rects()
    settings_rects = compute_settings_panel_rects()
    ranking_box_rect, ranking_back_rect = compute_ranking_panel_rects()
    credits_box_rect, credits_back_rect = compute_credits_panel_rects()
    menu_credits_chip_rect = compute_menu_credits_chip_rect()
    shop_box_rect, shop_item_rects, shop_back_rect = compute_shop_panel_rects(SKIN_CATALOG)
    menu_labels, menu_icons = main_menu_labels_and_icons()
    save_data = load_save_data()
    screen_state = GameScreen.INTRO
    intro = IntroState(menu_bg)
    session: RoundSession | None = None
    phys_accum = 0.0
    game_over_reason: str = ''
    strokes_used_victory = 0
    stars_victory = 0
    coins_earned_victory = 0
    defeat_bg, defeat_btn_menu, defeat_btn_retry, go_menu_rect, go_retry_rect = _load_game_over_assets()
    victory_bg, vic3_next_s, vic3_menu_s, vic3_retry_s, vic_r_next3, vic_r_menu3, vic_r_retry3, vic2_menu_s, vic2_retry_s, vic_r_menu2, vic_r_retry2 = _load_victory_assets_pack()
    pause_continuar_rect = _button_rect(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 24, 280, 48)
    pause_menu_rect = _button_rect(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 84, 260, 44)
    running = True
    while running:
        dt_ms = clock.tick(120)
        dt = dt_ms / 1000.0
        mouse_logical = presenter.window_to_logical(pygame.mouse.get_pos())
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                continue
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    settings.fullscreen = not settings.fullscreen
                    physical_screen = presenter.apply_video_mode(settings)
                    save_settings(settings)
                    continue
                if event.key == pygame.K_RETURN and event.mod & pygame.KMOD_ALT:
                    settings.fullscreen = not settings.fullscreen
                    physical_screen = presenter.apply_video_mode(settings)
                    save_settings(settings)
                    continue
                if not settings.fullscreen:
                    if event.key in (pygame.K_RIGHTBRACKET, pygame.K_EQUALS):
                        settings.window_scale += 1
                        settings.clamp()
                        physical_screen = presenter.apply_video_mode(settings)
                        save_settings(settings)
                        continue
                    if event.key in (pygame.K_LEFTBRACKET, pygame.K_MINUS):
                        settings.window_scale -= 1
                        settings.clamp()
                        physical_screen = presenter.apply_video_mode(settings)
                        save_settings(settings)
                        continue
            ev_mx, ev_my = mouse_logical
            if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
                ev_mx, ev_my = presenter.window_to_logical(event.pos)
            if screen_state == GameScreen.INTRO:
                if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                    if event.type == pygame.KEYDOWN and event.key not in (pygame.K_RETURN, pygame.K_SPACE):
                        continue
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button != 1:
                        continue
                    audio_stub.play_ui_confirm()
                    screen_state = GameScreen.MENU
            elif screen_state == GameScreen.MENU:
                opt_toggle_fs_rect, opt_back_rect = settings_rects
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    if menu_panel == MenuPanel.SETTINGS:
                        menu_panel = MenuPanel.MAIN
                    elif menu_panel == MenuPanel.RANKING:
                        menu_panel = MenuPanel.MAIN
                    elif menu_panel == MenuPanel.SHOP:
                        menu_panel = MenuPanel.MAIN
                    elif menu_panel == MenuPanel.CREDITS:
                        menu_panel = MenuPanel.MAIN
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if menu_panel == MenuPanel.MAIN:
                        if menu_credits_chip_rect.collidepoint(ev_mx, ev_my):
                            audio_stub.play_ui_confirm()
                            menu_panel = MenuPanel.CREDITS
                        elif menu_btn_rects[0].collidepoint(ev_mx, ev_my):
                            audio_stub.play_ui_confirm()
                            start_id = START_LEVEL_ID if START_LEVEL_ID in ('fase1', 'fase2', 'fase3') else 'fase1'
                            session = RoundSession.new(make_level_by_id(start_id))
                            phys_accum = 0.0
                            screen_state = GameScreen.PLAY
                        elif menu_btn_rects[1].collidepoint(ev_mx, ev_my):
                            audio_stub.play_ui_confirm()
                            menu_panel = MenuPanel.SETTINGS
                        elif menu_btn_rects[2].collidepoint(ev_mx, ev_my):
                            audio_stub.play_ui_confirm()
                            menu_panel = MenuPanel.RANKING
                        elif MENU_SHOP_BUTTON_ENABLED and menu_btn_rects[3].collidepoint(ev_mx, ev_my):
                            audio_stub.play_ui_confirm()
                            menu_panel = MenuPanel.SHOP
                        elif menu_btn_rects[len(menu_labels) - 1].collidepoint(ev_mx, ev_my):
                            running = False
                    elif menu_panel == MenuPanel.SETTINGS:
                        if opt_toggle_fs_rect.collidepoint(ev_mx, ev_my):
                            settings.fullscreen = not settings.fullscreen
                            physical_screen = presenter.apply_video_mode(settings)
                            save_settings(settings)
                        elif opt_back_rect.collidepoint(ev_mx, ev_my):
                            audio_stub.play_ui_confirm()
                            menu_panel = MenuPanel.MAIN
                    elif menu_panel == MenuPanel.RANKING:
                        if ranking_back_rect.collidepoint(ev_mx, ev_my):
                            audio_stub.play_ui_confirm()
                            menu_panel = MenuPanel.MAIN
                    elif menu_panel == MenuPanel.SHOP:
                        if shop_back_rect.collidepoint(ev_mx, ev_my):
                            audio_stub.play_ui_confirm()
                            menu_panel = MenuPanel.MAIN
                        else:
                            for rect, (skin_id, _name, cost) in zip(shop_item_rects, SKIN_CATALOG[1:]):
                                if not rect.collidepoint(ev_mx, ev_my):
                                    continue
                                if skin_id in save_data.unlocked_skins:
                                    if save_data.active_skin != skin_id:
                                        set_active_skin(save_data, skin_id)
                                        save_save_data(save_data)
                                        audio_stub.play_ui_confirm()
                                elif purchase_skin(save_data, skin_id, cost):
                                    save_save_data(save_data)
                                    audio_stub.play_ui_confirm()
                                break
                    elif menu_panel == MenuPanel.CREDITS:
                        if credits_back_rect.collidepoint(ev_mx, ev_my):
                            audio_stub.play_ui_confirm()
                            menu_panel = MenuPanel.MAIN
            elif screen_state == GameScreen.PLAY and session is not None:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    session.try_begin_aim(ev_mx, ev_my)
                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    session.release_shot(ev_mx, ev_my)
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    session.cancel_aim()
                    screen_state = GameScreen.PAUSED
            elif screen_state == GameScreen.VICTORY:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and (session is not None):
                    lid = session.level.id
                    if lid == 'fase3' and _victory_fase3_credits_btn_rect().collidepoint(ev_mx, ev_my):
                        audio_stub.play_ui_confirm()
                        session = None
                        screen_state = GameScreen.POST_GAME_CREDITS
                    elif lid in _VICTORY_CONTINUE_TO:
                        if vic_r_next3.collidepoint(ev_mx, ev_my):
                            audio_stub.play_ui_confirm()
                            nxt = _VICTORY_CONTINUE_TO.get(lid)
                            if nxt:
                                session = RoundSession.new(make_level_by_id(nxt))
                                phys_accum = 0.0
                                screen_state = GameScreen.PLAY
                        elif vic_r_menu3.collidepoint(ev_mx, ev_my):
                            audio_stub.play_ui_confirm()
                            menu_panel = MenuPanel.MAIN
                            screen_state = GameScreen.MENU
                        elif vic_r_retry3.collidepoint(ev_mx, ev_my):
                            audio_stub.play_ui_confirm()
                            session = RoundSession.new(make_level_by_id(lid))
                            phys_accum = 0.0
                            screen_state = GameScreen.PLAY
                    elif vic_r_menu2.collidepoint(ev_mx, ev_my):
                        audio_stub.play_ui_confirm()
                        menu_panel = MenuPanel.MAIN
                        screen_state = GameScreen.MENU
                    elif vic_r_retry2.collidepoint(ev_mx, ev_my):
                        audio_stub.play_ui_confirm()
                        session = RoundSession.new(make_level_by_id(lid))
                        phys_accum = 0.0
                        screen_state = GameScreen.PLAY
            elif screen_state == GameScreen.GAME_OVER:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and (session is not None):
                    if go_menu_rect.collidepoint(ev_mx, ev_my):
                        audio_stub.play_ui_confirm()
                        menu_panel = MenuPanel.MAIN
                        screen_state = GameScreen.MENU
                    elif go_retry_rect.collidepoint(ev_mx, ev_my):
                        audio_stub.play_ui_confirm()
                        session = RoundSession.new(make_level_by_id(session.level.id))
                        phys_accum = 0.0
                        screen_state = GameScreen.PLAY
            elif screen_state == GameScreen.PAUSED and session is not None:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    screen_state = GameScreen.PLAY
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if pause_continuar_rect.collidepoint(ev_mx, ev_my):
                        audio_stub.play_ui_confirm()
                        screen_state = GameScreen.PLAY
                    elif pause_menu_rect.collidepoint(ev_mx, ev_my):
                        audio_stub.play_ui_confirm()
                        session.cancel_aim()
                        menu_panel = MenuPanel.MAIN
                        screen_state = GameScreen.MENU
            elif screen_state == GameScreen.POST_GAME_CREDITS:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    screen_state = GameScreen.MENU
                    menu_panel = MenuPanel.MAIN
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if credits_back_rect.collidepoint(ev_mx, ev_my):
                        audio_stub.play_ui_confirm()
                        screen_state = GameScreen.MENU
                        menu_panel = MenuPanel.MAIN
        if screen_state == GameScreen.PLAY and session is not None and session.rolling:
            phys_accum += dt
            safety = 0
            while phys_accum >= FIXED_DT and safety < PHYS_ACCUM_LIMIT:
                safety += 1
                phys_accum -= FIXED_DT
                out = session.physics_step(FIXED_DT)
                if out == RoundOutcome.VICTORY:
                    strokes_used_victory = session.level.strokes - session.strokes_left
                    stars_victory = calc_stars(session.strokes_left, session.level.strokes)
                    update_best_score(save_data, session.level.id, stars_victory, strokes_used_victory)
                    coins_earned_victory = award_coins(save_data, stars_victory)
                    save_save_data(save_data)
                    screen_state = GameScreen.VICTORY
                    break
                if out == RoundOutcome.GAME_OVER_WATER:
                    game_over_reason = 'A bola caiu na água.'
                    screen_state = GameScreen.GAME_OVER
                    break
                if out == RoundOutcome.WATER_RESPAWN:
                    break
                if out == RoundOutcome.GAME_OVER_STROKES:
                    game_over_reason = 'Acabaram as tacadas.'
                    screen_state = GameScreen.GAME_OVER
                    break
        if screen_state == GameScreen.INTRO:
            intro.update()
            intro.draw(logical_screen, font_title, font_sub, font_ui)
        elif screen_state == GameScreen.MENU:
            draw_menu_background(logical_screen, menu_bg)
            if menu_panel == MenuPanel.MAIN:
                draw_main_menu_buttons(logical_screen, menu_font_btn, menu_btn_rects, menu_labels, menu_icons)
                draw_menu_credits_chip(logical_screen, menu_credits_chip_rect)
            elif menu_panel == MenuPanel.SETTINGS:
                draw_settings_overlay(logical_screen, menu_font_btn, menu_font_hint, settings, settings_rects)
            elif menu_panel == MenuPanel.RANKING:
                draw_ranking_overlay(logical_screen, menu_font_title, menu_font_btn, ranking_box_rect, ranking_back_rect, save_data)
            elif menu_panel == MenuPanel.SHOP:
                draw_shop_overlay(logical_screen, menu_font_title, menu_font_btn, menu_font_hint, shop_box_rect, shop_item_rects, shop_back_rect, SKIN_CATALOG, save_data)
            elif menu_panel == MenuPanel.CREDITS:
                draw_credits_overlay(logical_screen, menu_font_title, menu_font_btn, menu_font_hint, credits_box_rect, credits_back_rect)
        elif screen_state == GameScreen.PLAY and session is not None:
            logical_screen.fill((28, 26, 32))
            draw_playfield(logical_screen, session.level)
            draw_ball(logical_screen, session.ball_x, session.ball_y, save_data.active_skin)
            draw_programmatic_hole_and_flag(logical_screen, session.level)
            draw_aim(logical_screen, session, (int(mouse_logical[0]), int(mouse_logical[1])))
            draw_hud(logical_screen, font_ui, session, save_data.caju_coins)
        elif screen_state == GameScreen.VICTORY:
            logical_screen.blit(victory_bg, (0, 0))
            if session is not None and session.level.id in _VICTORY_CONTINUE_TO:
                logical_screen.blit(vic3_next_s, vic_r_next3.topleft)
                logical_screen.blit(vic3_menu_s, vic_r_menu3.topleft)
                logical_screen.blit(vic3_retry_s, vic_r_retry3.topleft)
            elif session is not None:
                logical_screen.blit(vic2_menu_s, vic_r_menu2.topleft)
                logical_screen.blit(vic2_retry_s, vic_r_retry2.topleft)
            if session is not None and session.level.id == 'fase3':
                vcr = _victory_fase3_credits_btn_rect()
                pygame.draw.rect(logical_screen, (52, 92, 62), vcr, border_radius=8)
                pygame.draw.rect(logical_screen, (130, 170, 120), vcr, width=2, border_radius=8)
                tcred = menu_font_hint.render('CREDITOS', True, (240, 250, 235))
                logical_screen.blit(tcred, tcred.get_rect(center=vcr.center))
        elif screen_state == GameScreen.POST_GAME_CREDITS:
            draw_credits_overlay(logical_screen, menu_font_title, menu_font_btn, menu_font_hint, credits_box_rect, credits_back_rect)
        elif screen_state == GameScreen.GAME_OVER:
            logical_screen.blit(defeat_bg, (0, 0))
            logical_screen.blit(defeat_btn_menu, go_menu_rect.topleft)
            logical_screen.blit(defeat_btn_retry, go_retry_rect.topleft)
            if 'água' in game_over_reason.lower():
                hint = font_ui.render(game_over_reason, True, (220, 235, 255))
                logical_screen.blit(hint, hint.get_rect(midbottom=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 10)))
        elif screen_state == GameScreen.PAUSED and session is not None:
            logical_screen.fill((28, 26, 32))
            draw_playfield(logical_screen, session.level)
            draw_ball(logical_screen, session.ball_x, session.ball_y, save_data.active_skin)
            draw_programmatic_hole_and_flag(logical_screen, session.level)
            draw_hud(logical_screen, font_ui, session, save_data.caju_coins)
            draw_pause_overlay(logical_screen, font_title, font_ui, pause_continuar_rect, pause_menu_rect)
        presenter.present(logical_screen, physical_screen)
        pygame.display.flip()
    pygame.quit()

def main() -> None:
    run()
