from __future__ import annotations
import io
import math
import random
import struct
import wave as _wave
import pygame

_RATE = 22050
_loaded = False
_cache: dict[str, pygame.mixer.Sound] = {}


def _apply_env(samples: list[float], attack: float, decay: float) -> list[float]:
    n = len(samples)
    attack_n = max(1, int(n * attack))
    out = []
    for i, s in enumerate(samples):
        if i < attack_n:
            env = i / attack_n
        else:
            env = max(0.0, 1.0 - ((i - attack_n) / max(1, n - attack_n)) * decay)
        out.append(s * env)
    return out


def _to_sound(samples: list[float], vol: float = 0.40) -> pygame.mixer.Sound:
    raw = bytearray(len(samples) * 2)
    for i, s in enumerate(samples):
        v = int(max(-1.0, min(1.0, s * vol)) * 32767)
        struct.pack_into('<h', raw, i * 2, v)
    buf = io.BytesIO()
    with _wave.open(buf, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(_RATE)
        wf.writeframes(bytes(raw))
    buf.seek(0)
    return pygame.mixer.Sound(buf)


def _build_slingshot() -> pygame.mixer.Sound:
    # Descending chirp — rubber being pulled back
    dur = 0.13
    n = int(_RATE * dur)
    f0, f1 = 380.0, 150.0
    samples = []
    for i in range(n):
        t = i / _RATE
        phase = 2 * math.pi * (f0 * t + (f1 - f0) / (2 * dur) * t * t)
        samples.append(math.sin(phase))
    return _to_sound(_apply_env(samples, attack=0.05, decay=0.85), vol=0.30)


def _build_shot() -> pygame.mixer.Sound:
    # Dry thud — ball struck by club
    dur = 0.10
    n = int(_RATE * dur)
    samples = []
    for i in range(n):
        t = i / _RATE
        low = math.sin(2 * math.pi * 180 * t)
        noise = random.uniform(-1.0, 1.0)
        samples.append(low * 0.55 + noise * 0.45)
    return _to_sound(_apply_env(samples, attack=0.005, decay=1.0), vol=0.55)


def _build_wall_hit() -> pygame.mixer.Sound:
    # Short tap — ball bouncing off a wall
    dur = 0.065
    n = int(_RATE * dur)
    samples = []
    for i in range(n):
        t = i / _RATE
        tone = math.sin(2 * math.pi * 520 * t)
        noise = random.uniform(-0.25, 0.25)
        samples.append(tone + noise)
    return _to_sound(_apply_env(samples, attack=0.01, decay=1.0), vol=0.32)


def _build_splash() -> pygame.mixer.Sound:
    # White noise burst — ball hits water
    dur = 0.32
    n = int(_RATE * dur)
    samples = [random.uniform(-1.0, 1.0) for _ in range(n)]
    return _to_sound(_apply_env(samples, attack=0.04, decay=0.72), vol=0.45)


def _build_ui_confirm() -> pygame.mixer.Sound:
    # Two rising tones — menu button click
    n1 = int(_RATE * 0.065)
    gap = int(_RATE * 0.015)
    n2 = int(_RATE * 0.065)
    s1 = [math.sin(2 * math.pi * 560 * i / _RATE) for i in range(n1)]
    s2 = [math.sin(2 * math.pi * 840 * i / _RATE) for i in range(n2)]
    samples = _apply_env(s1, attack=0.10, decay=0.90) + [0.0] * gap + _apply_env(s2, attack=0.10, decay=0.90)
    return _to_sound(samples, vol=0.28)


def _build_victory() -> pygame.mixer.Sound:
    # C5-E5-G5-C6 arpeggio — ball in hole
    notes = [523.25, 659.25, 783.99, 1046.50]
    note_dur = 0.11
    gap = int(_RATE * 0.018)
    samples: list[float] = []
    for freq in notes:
        n = int(_RATE * note_dur)
        s = [math.sin(2 * math.pi * freq * i / _RATE) for i in range(n)]
        samples += _apply_env(s, attack=0.08, decay=0.85)
        samples += [0.0] * gap
    return _to_sound(samples, vol=0.42)


def _ensure_loaded() -> None:
    global _loaded
    if _loaded:
        return
    _loaded = True
    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=_RATE, size=-16, channels=1, buffer=512)
        _cache['slingshot'] = _build_slingshot()
        _cache['shot'] = _build_shot()
        _cache['wall'] = _build_wall_hit()
        _cache['splash'] = _build_splash()
        _cache['ui'] = _build_ui_confirm()
        _cache['victory'] = _build_victory()
    except Exception:
        pass  # audio unavailable — game continues silently


def _play(key: str) -> None:
    _ensure_loaded()
    snd = _cache.get(key)
    if snd:
        snd.play()


def play_slingshot_pull() -> None:
    _play('slingshot')

def play_shot() -> None:
    _play('shot')

def play_wall_hit() -> None:
    _play('wall')

def play_water_splash() -> None:
    _play('splash')

def play_ui_confirm() -> None:
    _play('ui')

def play_victory() -> None:
    _play('victory')


# --- Música de fundo ---

def _music_path() -> str:
    from tour_teresina_golf.resource_path import asset
    return str(asset('tour_teresina_golf/assets/music.ogg'))

def start_music() -> None:
    _ensure_loaded()
    try:
        pygame.mixer.music.load(_music_path())
        pygame.mixer.music.set_volume(0.35)
        pygame.mixer.music.play(-1)
    except Exception:
        pass

def pause_music() -> None:
    try:
        pygame.mixer.music.pause()
    except Exception:
        pass

def unpause_music() -> None:
    try:
        pygame.mixer.music.unpause()
    except Exception:
        pass

def stop_music() -> None:
    try:
        pygame.mixer.music.stop()
    except Exception:
        pass
