from __future__ import annotations
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
SAVE_VERSION = 1
_PHASE_IDS = ('fase1', 'fase2', 'fase3')

@dataclass
class PhaseRecord:
    stars: int = 0
    strokes_used: int = 999

@dataclass
class SaveData:
    fase1: PhaseRecord = field(default_factory=PhaseRecord)
    fase2: PhaseRecord = field(default_factory=PhaseRecord)
    fase3: PhaseRecord = field(default_factory=PhaseRecord)
    caju_coins: int = 0
    unlocked_skins: list[str] = field(default_factory=lambda: ['default'])
    active_skin: str = 'default'
    save_version: int = SAVE_VERSION

    def record_for(self, level_id: str) -> PhaseRecord | None:
        return getattr(self, level_id, None)

def _save_path() -> Path:
    return Path(__file__).resolve().parent.parent / 'save_data.json'

def load_save_data() -> SaveData:
    path = _save_path()
    if not path.is_file():
        return SaveData()
    try:
        raw = json.loads(path.read_text(encoding='utf-8'))
        d = SaveData()
        for pid in _PHASE_IDS:
            entry = raw.get(pid, {})
            rec = PhaseRecord(stars=int(entry.get('stars', 0)), strokes_used=int(entry.get('strokes_used', 999)))
            setattr(d, pid, rec)
        d.caju_coins = max(0, int(raw.get('caju_coins', 0)))
        us = raw.get('unlocked_skins', ['default'])
        if isinstance(us, list) and all((isinstance(x, str) for x in us)) and (len(us) > 0):
            d.unlocked_skins = list(us)
            if 'default' not in d.unlocked_skins:
                d.unlocked_skins.insert(0, 'default')
        d.active_skin = str(raw.get('active_skin', 'default'))
        if d.active_skin not in d.unlocked_skins:
            d.active_skin = 'default'
        return d
    except (json.JSONDecodeError, OSError, TypeError, ValueError):
        return SaveData()

def save_save_data(data: SaveData) -> None:
    path = _save_path()
    out: dict = {'save_version': SAVE_VERSION, 'caju_coins': data.caju_coins, 'unlocked_skins': data.unlocked_skins, 'active_skin': data.active_skin}
    for pid in _PHASE_IDS:
        rec = data.record_for(pid)
        if rec is not None:
            out[pid] = asdict(rec)
    path.write_text(json.dumps(out, indent=2), encoding='utf-8')

def update_best_score(data: SaveData, level_id: str, stars: int, strokes_used: int) -> bool:
    rec = data.record_for(level_id)
    if rec is None:
        return False
    if stars > rec.stars or (stars == rec.stars and strokes_used < rec.strokes_used):
        rec.stars = stars
        rec.strokes_used = strokes_used
        return True
    return False

def award_coins(data: SaveData, stars: int) -> int:
    from tour_teresina_golf.config import COINS_PER_STAR
    earned = stars * COINS_PER_STAR
    data.caju_coins += earned
    return earned

def purchase_skin(data: SaveData, skin_id: str, cost: int) -> bool:
    if skin_id in data.unlocked_skins:
        return False
    if data.caju_coins < cost:
        return False
    data.caju_coins -= cost
    data.unlocked_skins.append(skin_id)
    return True

def set_active_skin(data: SaveData, skin_id: str) -> None:
    if skin_id in data.unlocked_skins:
        data.active_skin = skin_id
