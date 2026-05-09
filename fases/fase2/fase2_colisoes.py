"""Metadados da Fase 2 — mapa costeiro (arte nativa 1672×941).

Coordenadas na referência da imagem ``fase2.png``. O jogo escala para 960×540.

Spawn junto à passadeira inferior central; buraco na zona leste (atalho da ponte).
Substituir ``fase2_mapa_colisao.png`` por uma máscara B&W manual melhora a colisão.
"""

from __future__ import annotations

REFERENCIA_W = 1672
REFERENCIA_H = 941

LARGURA_FASE2 = REFERENCIA_W
ALTURA_FASE2 = REFERENCIA_H

SPAWN_FASE2 = (836, 905)
BURACO_FASE2 = (1320, 360)
BURACO_RAIO_NATIVO = 28
