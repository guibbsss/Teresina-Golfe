"""Loop principal e máquina de estados (Intro → Menu → Play → Vitória / Game Over)."""

from __future__ import annotations

from enum import Enum, auto

import pygame

from tour_teresina_golf import audio_stub
from tour_teresina_golf.config import (
    FIXED_DT,
    LOGICAL_H,
    LOGICAL_W,
    PHYS_ACCUM_LIMIT,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    TITLE,
)
from tour_teresina_golf.draw_play import (
    draw_aim,
    draw_ball,
    draw_hud,
    draw_playfield,
    draw_programmatic_hole_and_flag,
    draw_stars,
)
from tour_teresina_golf.intro_screen import IntroState
from tour_teresina_golf.config import START_LEVEL_ID
from tour_teresina_golf.level import make_level_by_id

_VICTORY_CONTINUE_TO: dict[str, str] = {"fase1": "fase2", "fase2": "fase3"}
from tour_teresina_golf.main_menu_ui import (
    MenuIcon,
    MenuPanel,
    compute_main_menu_button_rects,
    compute_ranking_panel_rects,
    compute_settings_panel_rects,
    draw_main_menu_buttons,
    draw_menu_background,
    draw_ranking_overlay,
    draw_settings_overlay,
    load_menu_background_surface,
    load_menu_pixel_fonts,
)
from tour_teresina_golf.play_round import RoundOutcome, RoundSession, calc_stars
from tour_teresina_golf.settings import load_settings, save_settings
from tour_teresina_golf.video import DisplayPresenter


class GameScreen(Enum):
    INTRO = auto()
    MENU = auto()
    PLAY = auto()
    VICTORY = auto()
    GAME_OVER = auto()


def _make_fonts() -> tuple[pygame.font.Font, pygame.font.Font, pygame.font.Font, pygame.font.Font]:
    pygame.font.init()
    title = pygame.font.SysFont("consolas", 52, bold=True)
    sub = pygame.font.SysFont("consolas", 22)
    ui = pygame.font.SysFont("consolas", 20)
    ui_big = pygame.font.SysFont("consolas", 26)
    return title, sub, ui, ui_big


def _button_rect(center_x: int, center_y: int, w: int, h: int) -> pygame.Rect:
    return pygame.Rect(0, 0, w, h).move(center_x - w // 2, center_y - h // 2)


def _victory_button_rects(level_id: str) -> tuple[pygame.Rect | None, pygame.Rect, pygame.Rect]:
    """Continuar (fase1→2, fase2→3), Menu, Jogar novamente."""
    cx = SCREEN_WIDTH // 2
    cy = SCREEN_HEIGHT // 2
    if level_id in _VICTORY_CONTINUE_TO:
        return (
            _button_rect(cx, cy + 24, 280, 44),
            _button_rect(cx, cy + 84, 260, 44),
            _button_rect(cx, cy + 144, 260, 44),
        )
    return (
        None,
        _button_rect(cx, cy + 56, 260, 48),
        _button_rect(cx, cy + 116, 260, 48),
    )


def run() -> None:
    pygame.init()
    pygame.display.set_caption(TITLE)

    settings = load_settings()
    presenter = DisplayPresenter()
    physical_screen = presenter.apply_video_mode(settings)

    logical_screen = pygame.Surface((LOGICAL_W, SCREEN_HEIGHT))

    clock = pygame.time.Clock()

    font_title, font_sub, font_ui, font_ui_big = _make_fonts()
    font_stars = pygame.font.SysFont("consolas", 36)

    menu_bg, _ = load_menu_background_surface()
    menu_font_title, menu_font_btn, menu_font_hint = load_menu_pixel_fonts()
    menu_panel = MenuPanel.MAIN
    menu_btn_rects = compute_main_menu_button_rects()
    settings_rects = compute_settings_panel_rects()
    ranking_box_rect, ranking_back_rect = compute_ranking_panel_rects()
    menu_labels = ("JOGAR", "CONFIGURACOES", "RANKING", "SAIR")
    menu_icons = (MenuIcon.PLAY, MenuIcon.GEAR, MenuIcon.TROPHY, MenuIcon.DOOR)

    screen_state = GameScreen.INTRO
    intro = IntroState(menu_bg)
    session: RoundSession | None = None
    phys_accum = 0.0
    game_over_reason: str = ""
    strokes_used_victory = 0
    stars_victory = 0

    go_menu_rect = _button_rect(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 56, 260, 48)
    go_retry_rect = _button_rect(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 116, 260, 48)

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
                if event.key == pygame.K_RETURN and (event.mod & pygame.KMOD_ALT):
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
            if event.type in (
                pygame.MOUSEBUTTONDOWN,
                pygame.MOUSEBUTTONUP,
                pygame.MOUSEMOTION,
            ):
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
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if menu_panel == MenuPanel.MAIN:
                        if menu_btn_rects[0].collidepoint(ev_mx, ev_my):
                            audio_stub.play_ui_confirm()
                            start_id = (
                                START_LEVEL_ID
                                if START_LEVEL_ID in ("fase1", "fase2", "fase3")
                                else "fase1"
                            )
                            session = RoundSession.new(make_level_by_id(start_id))
                            phys_accum = 0.0
                            screen_state = GameScreen.PLAY
                        elif menu_btn_rects[1].collidepoint(ev_mx, ev_my):
                            audio_stub.play_ui_confirm()
                            menu_panel = MenuPanel.SETTINGS
                        elif menu_btn_rects[2].collidepoint(ev_mx, ev_my):
                            audio_stub.play_ui_confirm()
                            menu_panel = MenuPanel.RANKING
                        elif menu_btn_rects[3].collidepoint(ev_mx, ev_my):
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

            elif screen_state == GameScreen.PLAY and session is not None:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    session.try_begin_aim(ev_mx, ev_my)
                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    session.release_shot(ev_mx, ev_my)
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    session.cancel_aim()
                    menu_panel = MenuPanel.MAIN
                    screen_state = GameScreen.MENU

            elif screen_state == GameScreen.VICTORY:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and session is not None:
                    vic_cont, vic_menu_rect, vic_retry_rect = _victory_button_rects(session.level.id)
                    if vic_cont is not None and vic_cont.collidepoint(ev_mx, ev_my):
                        audio_stub.play_ui_confirm()
                        nxt = _VICTORY_CONTINUE_TO.get(session.level.id)
                        if nxt:
                            session = RoundSession.new(make_level_by_id(nxt))
                            phys_accum = 0.0
                            screen_state = GameScreen.PLAY
                    elif vic_menu_rect.collidepoint(ev_mx, ev_my):
                        audio_stub.play_ui_confirm()
                        menu_panel = MenuPanel.MAIN
                        screen_state = GameScreen.MENU
                    elif vic_retry_rect.collidepoint(ev_mx, ev_my):
                        audio_stub.play_ui_confirm()
                        session = RoundSession.new(make_level_by_id(session.level.id))
                        phys_accum = 0.0
                        screen_state = GameScreen.PLAY

            elif screen_state == GameScreen.GAME_OVER:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and session is not None:
                    if go_menu_rect.collidepoint(ev_mx, ev_my):
                        audio_stub.play_ui_confirm()
                        menu_panel = MenuPanel.MAIN
                        screen_state = GameScreen.MENU
                    elif go_retry_rect.collidepoint(ev_mx, ev_my):
                        audio_stub.play_ui_confirm()
                        session = RoundSession.new(make_level_by_id(session.level.id))
                        phys_accum = 0.0
                        screen_state = GameScreen.PLAY

        mouse_logical = presenter.window_to_logical(pygame.mouse.get_pos())

        if screen_state == GameScreen.PLAY and session is not None and session.rolling:
            phys_accum += dt
            safety = 0
            while phys_accum >= FIXED_DT and safety < PHYS_ACCUM_LIMIT:
                safety += 1
                phys_accum -= FIXED_DT
                out = session.physics_step(FIXED_DT)
                if out == RoundOutcome.VICTORY:
                    strokes_used_victory = session.level.strokes - session.strokes_left
                    stars_victory = calc_stars(session.strokes_left)
                    screen_state = GameScreen.VICTORY
                    break
                if out == RoundOutcome.GAME_OVER_WATER:
                    game_over_reason = "A bola caiu na água."
                    screen_state = GameScreen.GAME_OVER
                    break
                if out == RoundOutcome.WATER_RESPAWN:
                    break
                if out == RoundOutcome.GAME_OVER_STROKES:
                    game_over_reason = "Acabaram as tacadas."
                    screen_state = GameScreen.GAME_OVER
                    break

        if screen_state == GameScreen.INTRO:
            intro.update()
            intro.draw(logical_screen, font_title, font_sub, font_ui)

        elif screen_state == GameScreen.MENU:
            draw_menu_background(logical_screen, menu_bg)
            if menu_panel == MenuPanel.MAIN:
                draw_main_menu_buttons(
                    logical_screen,
                    menu_font_btn,
                    menu_btn_rects,
                    menu_labels,
                    menu_icons,
                )
            elif menu_panel == MenuPanel.SETTINGS:
                draw_settings_overlay(
                    logical_screen,
                    menu_font_btn,
                    menu_font_hint,
                    settings,
                    settings_rects,
                )
            elif menu_panel == MenuPanel.RANKING:
                draw_ranking_overlay(
                    logical_screen,
                    menu_font_title,
                    menu_font_btn,
                    ranking_box_rect,
                    ranking_back_rect,
                )

        elif screen_state == GameScreen.PLAY and session is not None:
            logical_screen.fill((28, 26, 32))
            draw_playfield(logical_screen, session.level)
            draw_ball(logical_screen, session.ball_x, session.ball_y)
            draw_programmatic_hole_and_flag(logical_screen, session.level)
            draw_aim(logical_screen, session, (int(mouse_logical[0]), int(mouse_logical[1])))
            draw_hud(logical_screen, font_ui, session)

        elif screen_state == GameScreen.VICTORY:
            logical_screen.fill((28, 42, 32))
            t = font_title.render("Buraco!", True, (200, 255, 190))
            logical_screen.blit(t, t.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 48)))
            info = font_ui_big.render(f"Tacadas usadas: {strokes_used_victory}", True, (220, 235, 210))
            info_rect = info.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 8))
            logical_screen.blit(info, info_rect)
            draw_stars(logical_screen, font_stars, stars_victory, SCREEN_WIDTH // 2, info_rect.bottom + 12)

            vic_cont, vic_menu_rect, vic_retry_rect = (
                _victory_button_rects(session.level.id) if session is not None else (None, pygame.Rect(0, 0, 0, 0), pygame.Rect(0, 0, 0, 0))
            )
            labels: list[tuple[pygame.Rect, str]]
            if vic_cont is not None:
                labels = [(vic_cont, "Continuar"), (vic_menu_rect, "Menu"), (vic_retry_rect, "Jogar novamente")]
            else:
                labels = [(vic_menu_rect, "Menu"), (vic_retry_rect, "Jogar novamente")]
            for rect, label in labels:
                pygame.draw.rect(logical_screen, (52, 72, 52), rect, border_radius=8)
                pygame.draw.rect(logical_screen, (120, 160, 110), rect, width=2, border_radius=8)
                tx = font_ui.render(label, True, (240, 250, 235))
                logical_screen.blit(tx, tx.get_rect(center=rect.center))

        elif screen_state == GameScreen.GAME_OVER:
            logical_screen.fill((42, 28, 28))
            t = font_title.render("Game Over", True, (255, 190, 190))
            logical_screen.blit(t, t.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 48)))
            r = font_ui_big.render(game_over_reason, True, (235, 210, 210))
            logical_screen.blit(r, r.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 8)))

            for rect, label in ((go_menu_rect, "Menu"), (go_retry_rect, "Reiniciar fase")):
                pygame.draw.rect(logical_screen, (72, 48, 48), rect, border_radius=8)
                pygame.draw.rect(logical_screen, (160, 110, 100), rect, width=2, border_radius=8)
                tx = font_ui.render(label, True, (255, 235, 230))
                logical_screen.blit(tx, tx.get_rect(center=rect.center))

        presenter.present(logical_screen, physical_screen)
        pygame.display.flip()

    pygame.quit()


def main() -> None:
    run()
