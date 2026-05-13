"""Metadados da Fase 3 — caís / passerelles (arte nativa 1672×941).

Coordenadas na referência da imagem ``fase3.png``. O jogo escala para 960×540.

**Bola e buraco:** edita ``SPAWN_FASE3`` e ``BURACO_FASE3`` (pixels 1672×941).
Por defeito o jogo **usa só estes valores**; o mapa a cores não os substitui.

O ficheiro ``fase3_mapa_colisao.png`` a cores define vermelho=sólido e
amarelo=água (respawn). Verde/branco no PNG são opcionais para quem quiser
posições automáticas a partir das manchas: define
``FASE3_SPAWN_BURACO_DO_MAPA = True`` para o motor tentar alinhar às manchas
(``SPAWN_FASE3`` / ``BURACO_FASE3`` passam a ser *hints*).

Ver ``tour_teresina_golf.level._fase3_parse_color_zones``.
"""

from __future__ import annotations

REFERENCIA_W = 1672
REFERENCIA_H = 941

LARGURA_FASE3 = REFERENCIA_W
ALTURA_FASE3 = REFERENCIA_H

# Bola (spawn) e centro do buraco — pixels nativos 1672×941 (medir sobre fase3.png).
SPAWN_FASE3 = (188, 377)
BURACO_FASE3 = (1325, 140)
BURACO_RAIO_NATIVO = 28

# True = com mapa a cores, tenta posição a partir das manchas verde/branco do PNG
# (usa SPAWN/BURACO como referência). False = posições são **só** as tuplos acima.
FASE3_SPAWN_BURACO_DO_MAPA = False
