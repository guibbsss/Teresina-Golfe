"""Definição declarativa de fases (paredes AA, água, buraco, spawn)."""

from __future__ import annotations

import importlib.util
from collections import deque
from dataclasses import dataclass, field
from pathlib import Path

import pygame

from tour_teresina_golf.collision import CollisionGrid
from tour_teresina_golf.config import LOGICAL_H, LOGICAL_W


_REPO_ROOT = Path(__file__).resolve().parent.parent


def _load_fase_module(rel_py: Path, mod_name: str):
    path = _REPO_ROOT / "fases" / rel_py
    spec = importlib.util.spec_from_file_location(mod_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Não foi possível carregar {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _load_fase1_colisoes_module():
    return _load_fase_module(Path("fase1") / "fase1_colisoes.py", "fase1_colisoes")


def _load_fase2_colisoes_module():
    return _load_fase_module(Path("fase2") / "fase2_colisoes.py", "fase2_colisoes")


def _load_fase3_colisoes_module():
    return _load_fase_module(Path("fase3") / "fase3_colisoes.py", "fase3_colisoes")


def _scale_xy(xy: tuple[float, float], sx: float, sy: float) -> tuple[float, float]:
    return float(xy[0] * sx), float(xy[1] * sy)


@dataclass
class Level:
    id: str
    name: str
    strokes: int
    ball_spawn: tuple[float, float]
    hole_center: tuple[float, float]
    walls: list[pygame.Rect] = field(default_factory=list)
    obstacles: list[pygame.Rect] = field(default_factory=list)
    water: list[pygame.Rect] = field(default_factory=list)
    play_rect: pygame.Rect | None = None
    background: pygame.Surface | None = None
    """Se definido, desenha-se este fundo em vez do fairway procedural."""
    hide_solids_overlay: bool = False
    """Se True, não desenhar retângulos de colisão/água por cima do fundo."""
    hole_capture_radius: float | None = None
    """Raio lógico para vitória no buraco; None usa ``HOLE_CAPTURE_RADIUS`` global."""
    hole_win_speed_sq: float | None = None
    """Limite de velocidade ao quadrados para buraco; None usa global."""
    draw_programmatic_hole: bool = False
    """Se True, ``draw_programmatic_hole_and_flag`` desenha buraco + bandeira por cima do bitmap."""
    flag_sprite_path: Path | None = None
    """Caminho opcional para ``bandeira.png`` (alpha); None usa ``acessorios/bandeira.png``."""
    collision_grid: CollisionGrid | None = None
    """Se definido, a física usa colisão pixel do mapa em vez de ``walls``/``obstacles``."""
    water_grid: CollisionGrid | None = None
    """Opcional (fase 3): pixels marcados como zona de água (respawn ao spawn, sem game over)."""
    collision_debug_overlay: pygame.Surface | None = None
    """Imagem semi-transparente opcional para ``DEBUG_DRAW_PHASE_COLLISIONS``."""


def _derived_coastal_collision_surface(art_rgb: pygame.Surface) -> pygame.Surface:
    """
    Gera máscara B&W a partir da arte colorida (água azul / relva / edifícios → preto).
    As vias em cinza ficam brancas. Usado na fase 2 e 3 como fallback até haver PNG manual.
    """
    w, h = art_rgb.get_size()
    out = pygame.Surface((w, h))

    for yy in range(h):
        for xx in range(w):
            r, g, b, *_ = art_rgb.get_at((xx, yy))
            lum = (r + g + b) // 3
            mx = max(r, g, b)
            mn = min(r, g, b)
            sp = mx - mn

            solid = True
            if b >= r + 26 and b >= g + 10 and lum >= 38:
                solid = True
            elif g >= r + 22 and g >= b + 14 and sp > 18:
                solid = True
            elif r >= g + 28 and r >= b + 18 and lum < 185:
                solid = True
            elif sp <= 50 and 22 <= lum <= 228:
                solid = False

            c = (0, 0, 0) if solid else (255, 255, 255)
            out.set_at((xx, yy), c)
    return out


def _surface_to_collision_grid(surf: pygame.Surface, lum_threshold: int = 128) -> CollisionGrid:
    w, h = surf.get_size()
    buf = bytearray(w * h)
    for yy in range(h):
        base = yy * w
        for xx in range(w):
            c = surf.get_at((xx, yy))
            lum = (c[0] + c[1] + c[2]) // 3
            if lum < lum_threshold:
                buf[base + xx] = 1
    return CollisionGrid(width=w, height=h, solid=bytes(buf))


def _fase3_classify_zone(r: int, g: int, b: int) -> str | None:
    """Prioridade: branco, verde, amarelo, vermelho (marcadores antes de zonas de jogo)."""
    if r > 235 and g > 235 and b > 235:
        return "W"
    if g > 120 and b < 110 and r < 150 and (r + g) < 380 and g >= r + 25:
        return "G"
    if r > 180 and g > 180 and b < 120 and (r + g) > b + 200:
        return "Y"
    if r > 160 and g < 100 and b < 100 and r > g + 40 and r > b + 40:
        return "R"
    return None


def _fase3_connected_components(mask: bytearray, w: int, h: int) -> list[list[tuple[int, int]]]:
    vis = bytearray(w * h)
    out: list[list[tuple[int, int]]] = []
    for i in range(w * h):
        if not mask[i] or vis[i]:
            continue
        q: deque[int] = deque([i])
        vis[i] = 1
        pts: list[tuple[int, int]] = []
        while q:
            k = q.popleft()
            x, y = k % w, k // w
            pts.append((x, y))
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                x2, y2 = x + dx, y + dy
                if 0 <= x2 < w and 0 <= y2 < h:
                    k2 = y2 * w + x2
                    if mask[k2] and not vis[k2]:
                        vis[k2] = 1
                        q.append(k2)
        out.append(pts)
    return out


def _fase3_nearest_component_centroid(
    comps: list[list[tuple[int, int]]],
    hint: tuple[float, float],
    min_n: int,
    max_n: int,
    max_dist_sq: float,
) -> tuple[float, float] | None:
    """Escolhe o centroide do componente com tamanho em [min_n, max_n] mais próximo de ``hint``."""
    hx, hy = hint
    best: tuple[float, float] | None = None
    best_d = max_dist_sq
    for pts in comps:
        n = len(pts)
        if n < min_n or n > max_n:
            continue
        sx = sum(p[0] for p in pts) / n
        sy = sum(p[1] for p in pts) / n
        d = (sx - hx) * (sx - hx) + (sy - hy) * (sy - hy)
        if d < best_d:
            best_d = d
            best = (sx, sy)
    return best


def _fase3_parse_color_zones(
    zones_rgb: pygame.Surface,
    spawn_hint: tuple[float, float],
    hole_hint: tuple[float, float],
) -> tuple[pygame.Surface, pygame.Surface, tuple[float, float] | None, tuple[float, float] | None]:
    """
    Lê ``fase3_mapa_colisao.png`` a cores: vermelho=sólido, amarelo=água, verde=spawn, branco=buraco.
    Spawn e buraco: componentes verde/branco mais **próximos** de ``spawn_hint`` / ``hole_hint``
    (tipicamente ``SPAWN_FASE3`` / ``BURACO_FASE3`` em ``fase3_colisoes.py``), para não confundir
    relva com o marcador da plataforma esquerda.

    Devolve (máscara_sólidos, máscara_água, centro_spawn, centro_buraco) na resolução nativa;
    máscaras em branco=livre, preto=activo para ``_surface_to_collision_grid``.
    """
    w, h = zones_rgb.get_size()
    solid_m = bytearray(w * h)
    water_m = bytearray(w * h)
    green_m = bytearray(w * h)
    white_m = bytearray(w * h)

    for yy in range(h):
        base = yy * w
        for xx in range(w):
            r, g, b, *_ = zones_rgb.get_at((xx, yy))
            z = _fase3_classify_zone(r, g, b)
            if z == "R":
                solid_m[base + xx] = 1
            elif z == "Y":
                water_m[base + xx] = 1
            elif z == "G":
                green_m[base + xx] = 1
            elif z == "W":
                white_m[base + xx] = 1

    white = (255, 255, 255)
    black = (0, 0, 0)
    solid_surf = pygame.Surface((w, h))
    water_surf = pygame.Surface((w, h))
    for yy in range(h):
        base = yy * w
        for xx in range(w):
            solid_surf.set_at((xx, yy), black if solid_m[base + xx] else white)
            water_surf.set_at((xx, yy), black if water_m[base + xx] else white)

    g_comps = _fase3_connected_components(green_m, w, h)
    # Relva e canteiros geram muitos verdes; o spawn costuma ser o blob mais perto do hint (plataforma esquerda).
    spawn_c = _fase3_nearest_component_centroid(
        g_comps, spawn_hint, min_n=12, max_n=8000, max_dist_sq=(450.0 * 450.0)
    )
    if spawn_c is not None:
        dx = spawn_c[0] - spawn_hint[0]
        dy = spawn_c[1] - spawn_hint[1]
        if dx * dx + dy * dy > (110.0 * 110.0):
            spawn_c = None
    if spawn_c is None:
        spawn_c = spawn_hint

    w_comps = _fase3_connected_components(white_m, w, h)
    small: list[list[tuple[int, int]]] = []
    for pts in w_comps:
        n = len(pts)
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        bw, bh = max(xs) - min(xs) + 1, max(ys) - min(ys) + 1
        if 8 <= n <= 200 and max(bw, bh) <= 48:
            small.append(pts)
    hole_c = _fase3_nearest_component_centroid(
        small, hole_hint, min_n=8, max_n=200, max_dist_sq=(500.0 * 500.0)
    )
    if hole_c is None:
        hole_c = _fase3_nearest_component_centroid(
            w_comps, hole_hint, min_n=8, max_n=5000, max_dist_sq=(700.0 * 700.0)
        )
    if hole_c is not None:
        dx = hole_c[0] - hole_hint[0]
        dy = hole_c[1] - hole_hint[1]
        if dx * dx + dy * dy > (30.0 * 30.0):
            hole_c = None
    if hole_c is None:
        hole_c = hole_hint

    return solid_surf, water_surf, spawn_c, hole_c


def _fase3_looks_like_color_overlay(surf: pygame.Surface) -> bool:
    """Heurística: mapa a cores com faixas amarelas de água (fase 3)."""
    w, h = surf.get_size()
    n_y = 0
    for yy in range(0, h, 6):
        for xx in range(0, w, 6):
            r, g, b, *_ = surf.get_at((xx, yy))
            if r > 180 and g > 180 and b < 120 and (r + g) > b + 200:
                n_y += 1
    return n_y > 500


def make_fase1_level() -> Level:
    """Fase 1 — Av. Frei Serafim (colisões por retângulos definidos em fase1_colisoes.py)."""
    m = _load_fase1_colisoes_module()
    lw, lh = float(m.LARGURA_FASE1), float(m.ALTURA_FASE1)
    sx = LOGICAL_W / lw
    sy = LOGICAL_H / lh

    spawn = _scale_xy(m.SPAWN_FASE1, sx, sy)
    hole = _scale_xy(m.BURACO_FASE1, sx, sy)
    hole_cap = float(m.BURACO_RAIO_NATIVO) * min(sx, sy)

    img_path = _REPO_ROOT / "fases" / "fase1" / "fase1.png"
    if not img_path.is_file():
        raise FileNotFoundError(f"Arte da fase em falta: {img_path}")
    bg = pygame.image.load(str(img_path))
    if bg.get_size() != (LOGICAL_W, LOGICAL_H):
        bg = pygame.transform.smoothscale(bg, (LOGICAL_W, LOGICAL_H))
    if pygame.display.get_surface() is not None:
        bg = bg.convert()

    def _sr(xywh: tuple[int, int, int, int]) -> pygame.Rect:
        x, y, w, h = xywh
        return pygame.Rect(int(x * sx), int(y * sy), max(1, int(w * sx)), max(1, int(h * sy)))

    walls = [_sr(r) for r in m.PAREDES_FASE1]
    obstacles = [_sr(r) for r in m.OBSTACULOS_FASE1]

    return Level(
        id="fase1",
        name="Av. Frei Serafim",
        strokes=5,
        ball_spawn=spawn,
        hole_center=hole,
        walls=walls,
        obstacles=obstacles,
        water=[],
        play_rect=pygame.Rect(0, 0, LOGICAL_W, LOGICAL_H),
        background=bg,
        hide_solids_overlay=True,
        hole_capture_radius=hole_cap,
        draw_programmatic_hole=True,
        flag_sprite_path=_REPO_ROOT / "acessorios" / "bandeira.png",
        collision_grid=None,
    )


def make_fase2_level() -> Level:
    """Fase 2 — percurso costeiro (arte 1672×941; colisão bitmap ou derivada da arte)."""
    m = _load_fase2_colisoes_module()
    lw, lh = float(m.LARGURA_FASE2), float(m.ALTURA_FASE2)
    sx = LOGICAL_W / lw
    sy = LOGICAL_H / lh

    spawn = _scale_xy(m.SPAWN_FASE2, sx, sy)
    hole = _scale_xy(m.BURACO_FASE2, sx, sy)
    hole_cap = float(m.BURACO_RAIO_NATIVO) * min(sx, sy)

    img_path = _REPO_ROOT / "fases" / "fase2" / "fase2.png"
    if not img_path.is_file():
        raise FileNotFoundError(f"Arte da fase em falta: {img_path}")
    art_full = pygame.image.load(str(img_path))

    collision_bw_path = _REPO_ROOT / "fases" / "fase2" / "fase2_mapa_colisao.png"
    if collision_bw_path.is_file():
        col_full = pygame.image.load(str(collision_bw_path))
        if col_full.get_size() != art_full.get_size():
            col_full = pygame.transform.smoothscale(col_full, art_full.get_size())
    else:
        col_full = _derived_coastal_collision_surface(art_full)

    col_logic = pygame.transform.scale(col_full, (LOGICAL_W, LOGICAL_H))
    collision_grid = _surface_to_collision_grid(col_logic)
    dbg_overlay = col_logic.convert_alpha()
    dbg_overlay.set_alpha(85)

    bg = art_full
    if bg.get_size() != (LOGICAL_W, LOGICAL_H):
        bg = pygame.transform.smoothscale(bg, (LOGICAL_W, LOGICAL_H))
    if pygame.display.get_surface() is not None:
        bg = bg.convert()

    return Level(
        id="fase2",
        name="Marginal e ponte",
        strokes=7,
        ball_spawn=spawn,
        hole_center=hole,
        walls=[],
        obstacles=[],
        water=[],
        play_rect=pygame.Rect(0, 0, LOGICAL_W, LOGICAL_H),
        background=bg,
        hide_solids_overlay=True,
        hole_capture_radius=hole_cap,
        draw_programmatic_hole=True,
        flag_sprite_path=_REPO_ROOT / "acessorios" / "bandeira.png",
        collision_grid=collision_grid,
        collision_debug_overlay=dbg_overlay,
    )


def make_fase3_level() -> Level:
    """Fase 3 — mapa a cores: vermelho=sólido, amarelo=água (respawn), verde=spawn, branco=buraco."""
    m = _load_fase3_colisoes_module()
    lw, lh = float(m.LARGURA_FASE3), float(m.ALTURA_FASE3)
    sx = LOGICAL_W / lw
    sy = LOGICAL_H / lh

    spawn = _scale_xy(m.SPAWN_FASE3, sx, sy)
    hole = _scale_xy(m.BURACO_FASE3, sx, sy)
    hole_cap = float(m.BURACO_RAIO_NATIVO) * min(sx, sy)

    img_path = _REPO_ROOT / "fases" / "fase3" / "fase3.png"
    if not img_path.is_file():
        raise FileNotFoundError(f"Arte da fase em falta: {img_path}")
    art_full = pygame.image.load(str(img_path))

    collision_bw_path = _REPO_ROOT / "fases" / "fase3" / "fase3_mapa_colisao.png"
    water_grid: CollisionGrid | None = None

    if collision_bw_path.is_file():
        col_full = pygame.image.load(str(collision_bw_path))
        if col_full.get_size() != art_full.get_size():
            col_full = pygame.transform.smoothscale(col_full, art_full.get_size())
        if _fase3_looks_like_color_overlay(col_full):
            sh = (float(m.SPAWN_FASE3[0]), float(m.SPAWN_FASE3[1]))
            hh = (float(m.BURACO_FASE3[0]), float(m.BURACO_FASE3[1]))
            solid_native, water_native, sp_nat, ho_nat = _fase3_parse_color_zones(col_full, sh, hh)
            if getattr(m, "FASE3_SPAWN_BURACO_DO_MAPA", False) and sp_nat is not None:
                spawn = _scale_xy((sp_nat[0], sp_nat[1]), sx, sy)
            if getattr(m, "FASE3_SPAWN_BURACO_DO_MAPA", False) and ho_nat is not None:
                hole = _scale_xy((ho_nat[0], ho_nat[1]), sx, sy)
            solid_logic = pygame.transform.scale(solid_native, (LOGICAL_W, LOGICAL_H))
            water_logic = pygame.transform.scale(water_native, (LOGICAL_W, LOGICAL_H))
            collision_grid = _surface_to_collision_grid(solid_logic)
            water_grid = _surface_to_collision_grid(water_logic)
            dbg_overlay = solid_logic.convert_alpha()
            dbg_overlay.set_alpha(85)
        else:
            col_logic = pygame.transform.scale(col_full, (LOGICAL_W, LOGICAL_H))
            collision_grid = _surface_to_collision_grid(col_logic)
            dbg_overlay = col_logic.convert_alpha()
            dbg_overlay.set_alpha(85)
    else:
        col_full = _derived_coastal_collision_surface(art_full)
        col_logic = pygame.transform.scale(col_full, (LOGICAL_W, LOGICAL_H))
        collision_grid = _surface_to_collision_grid(col_logic)
        dbg_overlay = col_logic.convert_alpha()
        dbg_overlay.set_alpha(85)

    bg = art_full
    if bg.get_size() != (LOGICAL_W, LOGICAL_H):
        bg = pygame.transform.smoothscale(bg, (LOGICAL_W, LOGICAL_H))
    if pygame.display.get_surface() is not None:
        bg = bg.convert()

    return Level(
        id="fase3",
        name="Cais e passerelles",
        strokes=10,
        ball_spawn=spawn,
        hole_center=hole,
        walls=[],
        obstacles=[],
        water=[],
        play_rect=pygame.Rect(0, 0, LOGICAL_W, LOGICAL_H),
        background=bg,
        hide_solids_overlay=True,
        hole_capture_radius=hole_cap,
        draw_programmatic_hole=True,
        flag_sprite_path=_REPO_ROOT / "acessorios" / "bandeira.png",
        collision_grid=collision_grid,
        water_grid=water_grid,
        collision_debug_overlay=dbg_overlay,
    )


def make_level_by_id(level_id: str) -> Level:
    if level_id == "fase3":
        return make_fase3_level()
    if level_id == "fase2":
        return make_fase2_level()
    return make_fase1_level()
