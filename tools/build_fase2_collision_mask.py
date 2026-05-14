from __future__ import annotations
import os
import sys
import pygame
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T_DIFF = 55
DILATE_PASSES = 2

def _dilate8(mask: bytearray, w: int, h: int) -> bytearray:
    out = bytearray(mask)
    for y in range(h):
        for x in range(w):
            if mask[y * w + x]:
                continue
            hit = False
            for dy in (-1, 0, 1):
                yy = y + dy
                if yy < 0 or yy >= h:
                    continue
                for dx in (-1, 0, 1):
                    if dx == 0 and dy == 0:
                        continue
                    xx = x + dx
                    if xx < 0 or xx >= w:
                        continue
                    if mask[yy * w + xx]:
                        hit = True
                        break
                if hit:
                    break
            if hit:
                out[y * w + x] = 1
    return out

def main() -> None:
    os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
    pygame.init()
    pygame.display.set_mode((1, 1))
    path_a = os.path.join(ROOT, 'fases', 'fase2', 'fase2_mapa_colisoes.png')
    path_b = os.path.join(ROOT, 'fases', 'fase2', 'fase2.png')
    out_path = os.path.join(ROOT, 'fases', 'fase2', 'fase2_mapa_colisao.png')
    a = pygame.image.load(path_a).convert()
    b = pygame.image.load(path_b).convert()
    w, h = a.get_size()
    if b.get_size() != (w, h):
        print('ERRO: dimensões diferentes entre overlay e arte.', file=sys.stderr)
        sys.exit(1)
    mask = bytearray(w * h)
    for y in range(h):
        row = y * w
        for x in range(w):
            ca = a.get_at((x, y))
            cb = b.get_at((x, y))
            man = abs(ca[0] - cb[0]) + abs(ca[1] - cb[1]) + abs(ca[2] - cb[2])
            if man > T_DIFF:
                mask[row + x] = 1
    for _ in range(DILATE_PASSES):
        mask = _dilate8(mask, w, h)
    surf = pygame.Surface((w, h))
    for y in range(h):
        row = y * w
        for x in range(w):
            surf.set_at((x, y), (0, 0, 0) if mask[row + x] else (255, 255, 255))
    pygame.image.save(surf, out_path)
    print(f'Escrito {out_path} ({sum(mask)} pixeis sólidos).')
if __name__ == '__main__':
    main()
