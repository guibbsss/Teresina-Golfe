"""Metadados da Fase 3 — caís / passerelles (arte nativa 1672×941).

Coordenadas na referência da imagem ``fase3.png``. O jogo escala para 960×540.

Spawn na via vertical esquerda (zona do estacionamento); buraco no percurso inferior
direito rumo à casa. Substituir ``fase3_mapa_colisao.png`` melhora a precisão da colisão.
"""

from __future__ import annotations

REFERENCIA_W = 1672
REFERENCIA_H = 941

LARGURA_FASE3 = REFERENCIA_W
ALTURA_FASE3 = REFERENCIA_H

SPAWN_FASE3 = (115, 765)
BURACO_FASE3 = (1560, 850)
BURACO_RAIO_NATIVO = 28
