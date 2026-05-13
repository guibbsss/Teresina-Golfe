"""Definição declarativa de fases (paredes AA, água, buraco, spawn)."""

from __future__ import annotations

import importlib.util
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
        strokes=12,
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
        strokes=14,
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
    """Fase 3 — caís e passerelles (arte 1672×941; colisão bitmap ou derivada da arte)."""
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
        id="fase3",
        name="Cais e passerelles",
        strokes=14,
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


def make_level_by_id(level_id: str) -> Level:
    if level_id == "fase3":
        return make_fase3_level()
    if level_id == "fase2":
        return make_fase2_level()
    return make_fase1_level()
