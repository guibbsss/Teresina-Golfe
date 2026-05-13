"""Metadados da Fase 2 — mapa costeiro (arte nativa 1672×941).

Coordenadas na referência da imagem ``fase2.png``. O jogo escala para 960×540.

A máscara ``fase2_mapa_colisao.png`` (preto = sólido, branco = livre) é gerada a
partir de ``fase2_mapa_colisoes.png``: diferença de cor vs ``fase2.png``
(Manhattan RGB > 55) + 2 passos de dilatação 8-vizinhança; ver
``tools/build_fase2_collision_mask.py``.

Spawn e buraco alinhados aos marcadores na arte (rectângulo verde = bola,
quadrado branco = buraco), em coordenadas nativas 1672×941.
"""

from __future__ import annotations

REFERENCIA_W = 1672
REFERENCIA_H = 941

LARGURA_FASE2 = REFERENCIA_W
ALTURA_FASE2 = REFERENCIA_H

SPAWN_FASE2 = (215, 871)
BURACO_FASE2 = (1471, 205)
BURACO_RAIO_NATIVO = 28
