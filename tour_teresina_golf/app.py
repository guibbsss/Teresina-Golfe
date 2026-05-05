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
from tour_teresina_golf.draw_play import draw_aim, draw_ball, draw_hud, draw_playfield
from tour_teresina_golf.intro_screen import IntroState
from tour_teresina_golf.level import make_test_level
from tour_teresina_golf.play_round import RoundOutcome, RoundSession
from tour_teresina_golf.settings import load_settings, save_settings
from tour_teresina_golf.video import DisplayPresenter


class GameScreen(Enum):
    INTRO = auto()
    MENU = auto()
    OPTIONS = auto()
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


def run() -> None:
    pygame.init()
    pygame.display.set_caption(TITLE)

    settings = load_settings()
    presenter = DisplayPresenter()
    physical_screen = presenter.apply_video_mode(settings)

    logical_screen = pygame.Surface((LOGICAL_W, SCREEN_HEIGHT))

    clock = pygame.time.Clock()

    font_title, font_sub, font_ui, font_ui_big = _make_fonts()

    screen_state = GameScreen.INTRO
    intro = IntroState()
    session: RoundSession | None = None
    phys_accum = 0.0
    game_over_reason: str = ""
    strokes_used_victory = 0

    _mcy = SCREEN_HEIGHT // 2
    menu_play_rect = _button_rect(SCREEN_WIDTH // 2, _mcy - 52, 260, 48)
    menu_options_rect = _button_rect(SCREEN_WIDTH // 2, _mcy + 8, 260, 48)
    menu_quit_rect = _button_rect(SCREEN_WIDTH // 2, _mcy + 68, 260, 48)

    _ocy = SCREEN_HEIGHT // 2
    opt_toggle_fs_rect = _button_rect(SCREEN_WIDTH // 2, _ocy - 72, 340, 46)
    opt_scale_minus_rect = _button_rect(SCREEN_WIDTH // 2 - 88, _ocy + 8, 72, 40)
    opt_scale_plus_rect = _button_rect(SCREEN_WIDTH // 2 + 88, _ocy + 8, 72, 40)
    opt_back_rect = _button_rect(SCREEN_WIDTH // 2, _ocy + 88, 260, 46)

    vic_menu_rect = _button_rect(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 56, 260, 48)
    vic_retry_rect = _button_rect(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 116, 260, 48)

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
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if menu_play_rect.collidepoint(ev_mx, ev_my):
                        audio_stub.play_ui_confirm()
                        session = RoundSession.new(make_test_level())
                        phys_accum = 0.0
                        screen_state = GameScreen.PLAY
                    elif menu_options_rect.collidepoint(ev_mx, ev_my):
                        audio_stub.play_ui_confirm()
                        screen_state = GameScreen.OPTIONS
                    elif menu_quit_rect.collidepoint(ev_mx, ev_my):
                        running = False

            elif screen_state == GameScreen.OPTIONS:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if opt_toggle_fs_rect.collidepoint(ev_mx, ev_my):
                        settings.fullscreen = not settings.fullscreen
                        physical_screen = presenter.apply_video_mode(settings)
                        save_settings(settings)
                    elif opt_scale_minus_rect.collidepoint(ev_mx, ev_my) and not settings.fullscreen:
                        settings.window_scale -= 1
                        settings.clamp()
                        physical_screen = presenter.apply_video_mode(settings)
                        save_settings(settings)
                    elif opt_scale_plus_rect.collidepoint(ev_mx, ev_my) and not settings.fullscreen:
                        settings.window_scale += 1
                        settings.clamp()
                        physical_screen = presenter.apply_video_mode(settings)
                        save_settings(settings)
                    elif opt_back_rect.collidepoint(ev_mx, ev_my):
                        screen_state = GameScreen.MENU
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    screen_state = GameScreen.MENU

            elif screen_state == GameScreen.PLAY and session is not None:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    session.try_begin_aim(ev_mx, ev_my)
                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    session.release_shot(ev_mx, ev_my)
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    session.cancel_aim()
                    screen_state = GameScreen.MENU

            elif screen_state == GameScreen.VICTORY:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if vic_menu_rect.collidepoint(ev_mx, ev_my):
                        screen_state = GameScreen.MENU
                    elif vic_retry_rect.collidepoint(ev_mx, ev_my):
                        session = RoundSession.new(make_test_level())
                        phys_accum = 0.0
                        screen_state = GameScreen.PLAY

            elif screen_state == GameScreen.GAME_OVER:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if go_menu_rect.collidepoint(ev_mx, ev_my):
                        screen_state = GameScreen.MENU
                    elif go_retry_rect.collidepoint(ev_mx, ev_my):
                        session = RoundSession.new(make_test_level())
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
                    screen_state = GameScreen.VICTORY
                    break
                if out == RoundOutcome.GAME_OVER_WATER:
                    game_over_reason = "A bola caiu na água."
                    screen_state = GameScreen.GAME_OVER
                    break
                if out == RoundOutcome.GAME_OVER_STROKES:
                    game_over_reason = "Acabaram as tacadas."
                    screen_state = GameScreen.GAME_OVER
                    break

        if screen_state == GameScreen.INTRO:
            intro.update()
            intro.draw(logical_screen, font_title, font_sub, font_ui)

        elif screen_state == GameScreen.MENU:
            logical_screen.fill((36, 32, 40))
            title = font_title.render("Tour Teresina Golf", True, (255, 230, 190))
            logical_screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80)))
            subtitle = font_sub.render("PC · Mouse · Mini golfe urbano", True, (200, 180, 150))
            logical_screen.blit(subtitle, subtitle.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 36)))

            for rect, label in (
                (menu_play_rect, "Jogar"),
                (menu_options_rect, "Opções de vídeo"),
                (menu_quit_rect, "Sair"),
            ):
                pygame.draw.rect(logical_screen, (70, 58, 52), rect, border_radius=8)
                pygame.draw.rect(logical_screen, (130, 110, 90), rect, width=2, border_radius=8)
                tx = font_ui_big.render(label, True, (255, 245, 230))
                logical_screen.blit(tx, tx.get_rect(center=rect.center))

            hint = font_ui.render("Atalhos: F11 · Alt+Enter · [ ] ajustar escala (janela)", True, (140, 130, 120))
            logical_screen.blit(hint, hint.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 28)))

        elif screen_state == GameScreen.OPTIONS:
            logical_screen.fill((32, 30, 38))
            tit = font_title.render("Opções de vídeo", True, (255, 230, 200))
            logical_screen.blit(tit, tit.get_rect(center=(SCREEN_WIDTH // 2, 96)))

            fs_label = "Ecrã inteiro: ligado" if settings.fullscreen else "Ecrã inteiro: desligado"
            pygame.draw.rect(logical_screen, (56, 48, 62), opt_toggle_fs_rect, border_radius=8)
            pygame.draw.rect(logical_screen, (120, 100, 130), opt_toggle_fs_rect, width=2, border_radius=8)
            t_fs = font_ui_big.render(fs_label, True, (245, 235, 255))
            logical_screen.blit(t_fs, t_fs.get_rect(center=opt_toggle_fs_rect.center))

            win_w = LOGICAL_W * settings.window_scale
            win_h = LOGICAL_H * settings.window_scale
            if settings.fullscreen:
                res_line = "Modo janela: escolha escala abaixo ao voltar para janela."
                scale_line = "Em ecrã inteiro o jogo adapta-se ao monitor (960×540 lógico)."
            else:
                res_line = f"Tamanho da janela: {win_w} × {win_h} px (escala {settings.window_scale}×)"
                scale_line = "Menor / Maior alteram o tamanho da janela (1× = 960×540)."
            logical_screen.blit(font_ui.render(res_line, True, (210, 200, 220)), (40, _ocy - 28))
            logical_screen.blit(font_sub.render(scale_line, True, (160, 150, 175)), (40, _ocy - 4))

            dim_fs = settings.fullscreen
            sm_col = (38, 44, 48) if dim_fs else (52, 62, 72)
            sm_border = (55, 65, 72) if dim_fs else (90, 110, 125)
            txt_dim = (120, 125, 130) if dim_fs else (230, 240, 250)
            pygame.draw.rect(logical_screen, sm_col, opt_scale_minus_rect, border_radius=6)
            pygame.draw.rect(logical_screen, sm_border, opt_scale_minus_rect, width=1, border_radius=6)
            minus_surf = font_ui_big.render("-", True, txt_dim)
            logical_screen.blit(minus_surf, minus_surf.get_rect(center=opt_scale_minus_rect.center))

            pygame.draw.rect(logical_screen, sm_col, opt_scale_plus_rect, border_radius=6)
            pygame.draw.rect(logical_screen, sm_border, opt_scale_plus_rect, width=1, border_radius=6)
            plus_surf = font_ui_big.render("+", True, txt_dim)
            logical_screen.blit(plus_surf, plus_surf.get_rect(center=opt_scale_plus_rect.center))

            pygame.draw.rect(logical_screen, (58, 52, 48), opt_back_rect, border_radius=8)
            pygame.draw.rect(logical_screen, (130, 118, 105), opt_back_rect, width=2, border_radius=8)
            t_back = font_ui.render("Voltar ao menu", True, (255, 248, 235))
            logical_screen.blit(t_back, t_back.get_rect(center=opt_back_rect.center))

            foot = font_ui.render("Esc volta ao menu · alterações gravadas em user_settings.json", True, (120, 115, 130))
            logical_screen.blit(foot, foot.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 24)))

        elif screen_state == GameScreen.PLAY and session is not None:
            logical_screen.fill((28, 26, 32))
            draw_playfield(logical_screen, session.level)
            draw_ball(logical_screen, session.ball_x, session.ball_y)
            draw_aim(logical_screen, session, (int(mouse_logical[0]), int(mouse_logical[1])))
            draw_hud(logical_screen, font_ui, session)

        elif screen_state == GameScreen.VICTORY:
            logical_screen.fill((28, 42, 32))
            t = font_title.render("Buraco!", True, (200, 255, 190))
            logical_screen.blit(t, t.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 48)))
            info = font_ui_big.render(f"Tacadas usadas: {strokes_used_victory}", True, (220, 235, 210))
            logical_screen.blit(info, info.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 8)))

            for rect, label in ((vic_menu_rect, "Menu"), (vic_retry_rect, "Jogar novamente")):
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
