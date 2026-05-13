"""Metadados da Fase 1 — Av. Frei Serafim.

Coordenadas na referencia **1920x1080** (16:9). O jogo escala para 960x540 com
sx = 960/1920, sy = 540/1080.

As caixas foram obtidas a partir de ``fase1_mapa_colisoes.png`` (1672x941):
pixeis onde o mapa difere de ``fase1.png`` com distancia de cor > 55 (Manhattan),
componentes conexas para o canteiro e floreiras; paredes exteriores alinhadas
as faixas horizontais/verticais de diff (bordos vermelhos) e ao corredor a
direita (x >= 1625 no PNG).

Estrutura do percurso:
  Faixa superior (ate ~y 259): edificios e calcada.
  Canteiro central e floreiras: obstaculos no meio da via.
  Faixa inferior (a partir de ~y 791): edificios e calcada.
  Corredor direito estreito: entre o canteiro e a parede direita.
"""

from __future__ import annotations

REFERENCIA_W = 1920
REFERENCIA_H = 1080

LARGURA_FASE1 = REFERENCIA_W
ALTURA_FASE1 = REFERENCIA_H

SPAWN_FASE1 = (326, 713)
BURACO_FASE1 = (1555, 335)
BURACO_RAIO_NATIVO = 30

# ---------------------------------------------------------------------------
# Paredes — edificios e calcadas  (x, y, largura, altura) em 1920x1080
# ---------------------------------------------------------------------------
PAREDES_FASE1: list[tuple[int, int, int, int]] = [
    (0, 0, 1920, 259),      # faixa superior
    (0, 791, 1920, 289),    # faixa inferior
    (0, 259, 68, 531),      # bloco esquerdo (via ate ao canteiro)
    (1866, 259, 54, 531),   # bloco direito (corredor ate ao limite do mapa)
]

# ---------------------------------------------------------------------------
# Obstaculos — canteiro central, floreiras e pequenos postes (1920x1080)
# ---------------------------------------------------------------------------
OBSTACULOS_FASE1: list[tuple[int, int, int, int]] = [
    (199, 465, 1370, 133),   # canteiro central (ilha com arvores)
    (310, 336, 125, 64),    # floreira / bloco, faixa superior esquerda
    (1198, 336, 114, 60),   # floreira, faixa superior direita
    (788, 353, 33, 31),     # poste pequeno junto ao canteiro superior
    (598, 321, 185, 62),    # floreira maior, faixa superior centro-esquerda
    (1342, 388, 124, 65),   # floreira, faixa superior centro-direita
    (946, 603, 181, 76),    # floreira, faixa inferior esquerda-centro
    (697, 652, 117, 63),    # floreira, faixa inferior centro
    (1443, 644, 104, 71),   # floreira, faixa inferior direita
]
