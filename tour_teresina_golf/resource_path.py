from __future__ import annotations
import sys
from pathlib import Path


def _asset_base() -> Path:
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent.parent


def asset(relative: str) -> Path:
    return _asset_base() / relative


def data_dir() -> Path:
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent
