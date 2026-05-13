"""Persistência de progresso do jogador (melhores resultados por fase)."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

SAVE_VERSION = 1
_PHASE_IDS = ("fase1", "fase2", "fase3")


@dataclass
class PhaseRecord:
    stars: int = 0  # 0 = não jogada, 1–3 = melhor resultado
    strokes_used: int = 999  # melhor (menor) número de tacadas usadas


@dataclass
class SaveData:
    fase1: PhaseRecord = field(default_factory=PhaseRecord)
    fase2: PhaseRecord = field(default_factory=PhaseRecord)
    fase3: PhaseRecord = field(default_factory=PhaseRecord)
    save_version: int = SAVE_VERSION

    def record_for(self, level_id: str) -> PhaseRecord | None:
        return getattr(self, level_id, None)


def _save_path() -> Path:
    """Ficheiro JSON na raiz do repositório (irmão de ``main.py``)."""
    return Path(__file__).resolve().parent.parent / "save_data.json"


def load_save_data() -> SaveData:
    path = _save_path()
    if not path.is_file():
        return SaveData()
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        d = SaveData()
        for pid in _PHASE_IDS:
            entry = raw.get(pid, {})
            rec = PhaseRecord(
                stars=int(entry.get("stars", 0)),
                strokes_used=int(entry.get("strokes_used", 999)),
            )
            setattr(d, pid, rec)
        return d
    except (json.JSONDecodeError, OSError, TypeError, ValueError):
        return SaveData()


def save_save_data(data: SaveData) -> None:
    path = _save_path()
    out: dict = {"save_version": SAVE_VERSION}
    for pid in _PHASE_IDS:
        rec = data.record_for(pid)
        if rec is not None:
            out[pid] = asdict(rec)
    path.write_text(json.dumps(out, indent=2), encoding="utf-8")


def update_best_score(
    data: SaveData, level_id: str, stars: int, strokes_used: int
) -> bool:
    """Atualiza o recorde se o resultado atual for melhor. Retorna True se houve melhoria."""
    rec = data.record_for(level_id)
    if rec is None:
        return False
    if stars > rec.stars or (stars == rec.stars and strokes_used < rec.strokes_used):
        rec.stars = stars
        rec.strokes_used = strokes_used
        return True
    return False
