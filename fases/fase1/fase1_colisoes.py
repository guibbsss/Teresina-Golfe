"""Metadados da Fase 1 — Av. Frei Serafim.

Coordenadas na referência **1920×1080** (16:9). O jogo escala para 960×540 com
sx = 960/1920, sy = 540/1080.

Spawn / buraco alinhados aos marcadores (~17%/66% e ~81%/31% na arte 1080p).
A geometria sólida vem de ``fase1_mapa_colisao.png`` (bitmap em ``level.py``).
"""

from __future__ import annotations

# Referência de desenho das colisões e da arte exportada em Full HD
REFERENCIA_W = 1920
REFERENCIA_H = 1080

# Mantém compat com level.py (make_fase1_level usa estes nomes)
LARGURA_FASE1 = REFERENCIA_W
ALTURA_FASE1 = REFERENCIA_H

# Marcadores na arte 1920×1080 (bola à esquerda em baixo; buraco/bandeira à direita em cima)
SPAWN_FASE1 = (326, 713)
BURACO_FASE1 = (1555, 335)
BURACO_RAIO_NATIVO = 30
