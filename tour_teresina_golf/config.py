"""Constantes globais e paleta (referência: GDD — clima quente, asfalto, áreas verdes)."""

from __future__ import annotations

# Resolução lógica (simulação e níveis; o vídeo escala isto para o ecrã)
LOGICAL_W = 960
LOGICAL_H = 540
SCREEN_WIDTH = LOGICAL_W
SCREEN_HEIGHT = LOGICAL_H
TITLE = "Tour Teresina Golf"

# Desenvolvimento: True desenha retângulos de colisão da fase a vermelho durante o jogo
DEBUG_DRAW_PHASE_COLLISIONS = True

# Nível ao clicar «Jogar» no menu: None ou "fase1" = começar na fase 1; "fase2" / "fase3" para testes.
# Também podes usar: python main.py fase3
START_LEVEL_ID: str | None = None

# Simulação
FIXED_DT = 1.0 / 120.0
MAX_PHYS_STEPS = 12
# Limite de passos de física por frame (evita espiral se o relógio atrasar)
PHYS_ACCUM_LIMIT = 256

# Bola
BALL_RADIUS = 6
MAX_SPEED = 2800.0
RESTITUTION = 0.72
FRICTION_PER_SEC = 2.15

# Tacada (estilingue): arrasto normalizado entre deadzone e MAX_DRAG_LEN → velocidade linear até MAX_SHOT_SPEED
AIM_GRAB_RADIUS = 52
MIN_DRAG_SHOT = 4  # deadzone (px); abaixo disto cancela sem tacada
MAX_DRAG_LEN = 220
# Antigo teto: MAX_DRAG_LEN * POWER_SCALE ≈ 3190 px/s de magnitude inicial
MAX_SHOT_SPEED = MAX_DRAG_LEN * 14.5

# Buraco
HOLE_CAPTURE_RADIUS = 22
# Paragem numérica (bola “idle” para pegar na mão / proxima tacada)
STOP_SPEED_SQ = 24.0 * 24.0
# Vitória com bola ainda a mover-se lentamente dentro do raio (GDD: velocidade baixa)
HOLE_WIN_SPEED_SQ = 85.0 * 85.0

# Cores — gameplay placeholder alinhado a moodboard urbano / verde (sec. 6 GDD)
COLOR_BG_TOP = (255, 178, 102)
COLOR_BG_BOTTOM = (92, 58, 42)
COLOR_FAIRWAY = (52, 112, 72)
COLOR_FAIRWAY_ALT = (44, 98, 62)
COLOR_ASPHALT = (48, 48, 54)
COLOR_WALL = (72, 62, 58)
COLOR_WATER = (38, 92, 158)
COLOR_WATER_SHALLOW = (70, 140, 190)
COLOR_HOLE = (18, 18, 22)
COLOR_HOLE_RING = (240, 240, 235)
COLOR_BALL = (245, 245, 245)
COLOR_BALL_SHADOW = (0, 0, 0, 90)
COLOR_UI_TEXT = (255, 248, 235)
COLOR_UI_ACCENT = (255, 214, 120)

# Intro / UI
INTRO_TITLE_COLOR = (255, 235, 200)
INTRO_SUB_COLOR = (255, 200, 140)
