from __future__ import annotations
import math
from tour_teresina_golf.config import FRICTION_PER_SEC, MAX_SPEED, STOP_SPEED_SQ

def apply_friction(vx: float, vy: float, dt: float) -> tuple[float, float]:
    k = FRICTION_PER_SEC
    factor = math.exp(-k * dt)
    vx *= factor
    vy *= factor
    return (vx, vy)

def clamp_speed(vx: float, vy: float) -> tuple[float, float]:
    s2 = vx * vx + vy * vy
    max_s = MAX_SPEED
    if s2 > max_s * max_s:
        s = math.sqrt(s2)
        scale = max_s / s
        return (vx * scale, vy * scale)
    return (vx, vy)

def is_stopped(vx: float, vy: float) -> bool:
    return vx * vx + vy * vy < STOP_SPEED_SQ
