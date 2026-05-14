from __future__ import annotations
import json
from dataclasses import asdict, dataclass
from pathlib import Path
SETTINGS_FILE_VERSION = 1

@dataclass
class UserSettings:
    fullscreen: bool = False
    window_scale: int = 2
    settings_version: int = SETTINGS_FILE_VERSION

    def clamp(self) -> None:
        self.window_scale = max(1, min(6, int(self.window_scale)))

def settings_path() -> Path:
    from tour_teresina_golf.resource_path import data_dir
    return data_dir() / 'user_settings.json'

def load_settings() -> UserSettings:
    path = settings_path()
    if not path.is_file():
        s = UserSettings()
        s.clamp()
        return s
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
        ver = data.get('settings_version')
        ws = int(data.get('window_scale', 2))
        fs = bool(data.get('fullscreen', False))
        if ver is None:
            fs = False
        s = UserSettings(fullscreen=fs, window_scale=ws, settings_version=SETTINGS_FILE_VERSION)
        s.clamp()
        if ver is None:
            save_settings(s)
        return s
    except (json.JSONDecodeError, OSError, TypeError, ValueError):
        s = UserSettings()
        s.clamp()
        return s

def save_settings(s: UserSettings) -> None:
    s.clamp()
    s.settings_version = SETTINGS_FILE_VERSION
    path = settings_path()
    path.write_text(json.dumps(asdict(s), indent=2), encoding='utf-8')
