"""Sprites originais em baixa resolução, compartilhados entre jogo e menus."""

from functools import lru_cache

import pygame


INK = (27, 28, 43)
BERRY = (154, 39, 70)
BLUE = (44, 83, 155)
LOOKS = {
    "boy": ((40, 31, 41), (242, 172, 116), "tuft"),
    "girl": ((72, 40, 52), (223, 149, 108), "tails"),
    "Levi": ((44, 32, 42), (211, 146, 104), "tuft"),
    "Reidryan": ((31, 26, 43), (156, 98, 73), "round"),
    "Bruno": ((112, 63, 42), (244, 183, 137), "sweep"),
    "Davi": ((38, 27, 40), (188, 116, 82), "fade"),
    "Jaylson": ((68, 40, 34), (218, 151, 100), "round"),
    "Jota": ((30, 37, 48), (139, 87, 65), "fade"),
    "Rafa": ((103, 48, 38), (230, 151, 100), "tuft"),
    "Bia": ((43, 28, 55), (187, 122, 86), "tails"),
    "Alex": ((45, 44, 68), (237, 185, 143), "sweep"),
    "Prof. André": ((110, 109, 124), (216, 153, 111), "sweep"),
    "Professora Marta": ((74, 46, 65), (229, 160, 112), "bob"),
    "Seu Damião": ((110, 107, 103), (158, 110, 82), "fade"),
    "Dona Celina": ((62, 45, 54), (191, 127, 95), "round"),
}
STAFF = {
    "Prof. André": ((69, 50, 75), (159, 106, 88)),
    "Professora Marta": ((39, 96, 99), (96, 166, 150)),
    "Seu Damião": ((54, 95, 79), (124, 173, 106)),
    "Dona Celina": ((125, 68, 80), (215, 143, 100)),
}


def shade(color, delta):
    return tuple(max(0, min(255, channel+delta)) for channel in color)


@lru_cache(maxsize=256)
def sprite(name, facing="down", pose="idle", frame=0):
    image = pygame.Surface((32, 40), pygame.SRCALPHA)
    hair, skin, cut = LOOKS[name]
    sleeves, jacket = STAFF.get(name, (BERRY, BLUE))
    side = facing == "side"
    back = facing == "up"
    lift = int(pose == "walk" and frame % 4 != 0)
    lean = 2 if pose == "dash" and side else -1 if pose == "hurt" else 0

    def box(color, x, y, w, h):
        pygame.draw.rect(image, color, (x+lean, y-lift, w, h))

    def shape(color, points):
        pygame.draw.polygon(image, color, [(x+lean, y-lift) for x, y in points])

    stride = (0, 2, 0, -2)[frame % 4] if pose == "walk" else 0
    legs = ((11, 0), (17, 0))
    if side:
        legs = ((12-stride, 0), (16+stride, 0))
    elif stride:
        legs = ((11, -stride), (17, stride))
    for x, y in legs:
        box(INK, x, 29+y, 6, 9)
        box((55, 60, 84), x+1, 30+y, 4, 5)
        box((221, 216, 208), x+1, 35+y, 4, 2)
    shape(INK, ((8, 19), (23, 19), (26, 23), (25, 31), (8, 31), (6, 24)))
    box(shade(sleeves, -20), 8, 21, 16, 9)
    box(sleeves, 9, 21, 14, 7)
    box(shade(jacket, -28), 11, 20, 10, 10)
    box(jacket, 12, 21, 8, 7)
    box(shade(jacket, 28), 12, 21, 7, 2)
    if back:
        box((48, 54, 82), 11, 22, 10, 8)
        box((79, 103, 140), 12, 22, 8, 5)
    elif not side:
        box((229, 220, 193), 14, 22, 4, 2)
        box((235, 177, 92), 18, 25, 2, 2)
    else:
        box(shade(sleeves, 32), 10, 23, 2, 5)
    for x, offset in ((6, stride//2), (22, -stride//2)):
        y = 22+offset
        if x == 22 and pose in ("punch", "wave", "throw"):
            if pose == "throw":
                y = 11 if frame == 0 else 20 if side else 13 if back else 25
            else:
                y = 15 if pose == "wave" else (22 if frame == 0 else 17 if back else 25)
            x += 3 if side or pose in ("wave", "throw") else 1
            box(INK, x, y, 6, 7)
            box(skin, x+1, y+1, 4, 4)
        else:
            box(INK, x, y, 5, 8)
            box(sleeves, x+1, y+1, 3, 4)
            box(skin, x+1, y+5, 3, 2)

    if cut in ("tails", "bob"):
        shape(INK, ((8, 8), (4, 13), (4, 22), (8, 24), (10, 19), (22, 19), (26, 24), (29, 22), (27, 12), (23, 7)))
        box(hair, 5, 14, 4, 8)
        box(shade(hair, 16), 24, 13, 3, 8)
    shape(INK, ((8, 6), (11, 3), (21, 3), (25, 7), (25, 12), (27, 13), (27, 17),
                (24, 18), (22, 21), (10, 21), (7, 18), (5, 17), (5, 13), (8, 12)))
    box(skin, 8, 10, 16, 8)
    box(shade(skin, -22), 10, 18, 12, 2)
    box(shade(skin, 19), 10, 12, 8, 3)
    box(shade(skin, -12), 6, 14, 3, 3)
    box(shade(skin, -12), 23, 14, 3, 3)
    shape(hair, ((8, 10), (9, 6), (12, 4), (20, 4), (24, 8), (24, 13), (21, 11), (11, 12), (8, 14)))
    if cut == "tuft":
        box(INK, 13, 1, 8, 4)
        box(shade(hair, 28), 14, 2, 6, 3)
    elif cut == "round":
        box(hair, 10, 4, 12, 7)
        for x in (10, 14, 18, 21):
            box(shade(hair, 28), x, 5+(x % 3), 2, 2)
    elif cut == "sweep":
        shape(shade(hair, 23), ((9, 7), (15, 4), (22, 5), (20, 8), (12, 11), (9, 11)))
    else:
        box(shade(hair, 22), 10, 6, 11, 3)

    if back:
        box(hair, 8, 10, 16, 8)
        box(shade(hair, 22), 10, 9, 10, 3)
    else:
        eyes = (18,) if side else (11, 19)
        for x in eyes:
            box(INK, x, 14, 3, 1 if pose in ("blink", "hurt") else 2)
            if pose not in ("blink", "hurt"):
                box((251, 239, 217), x, 14, 1, 1)
        box(shade(skin, -38), 19 if side else 15, 17, 3, 1)
        if pose == "talk":
            box((107, 54, 54), 19 if side else 15, 17, 3, 2)
        if pose == "hurt" or name == "Prof. André":
            box(INK, 12, 12, 3, 1)
            box(INK, 19, 12, 3, 1)
        if name in ("Reidryan", "Bia", "Prof. André"):
            box((74, 142, 158), 10, 13, 13, 1)
            box((74, 142, 158), 10, 14, 1, 3)
            box((74, 142, 158), 22, 14, 1, 3)
    if name == "Rafa" and not back:
        box((225, 72, 88), 8, 9, 16, 2)
    if name == "Alex":
        box((218, 235, 238), 10, 21, 13, 2)
    if name == "Seu Damião":
        box((75, 118, 105), 7, 5, 18, 4)
        box((107, 155, 131), 10, 4, 11, 3)
    if pose == "block":
        y = 19 if frame else 22
        box(INK, 8, y, 16, 5)
        box(shade(sleeves, 22), 9, y+1, 14, 3)
        box(skin, 12, y+1, 6, 3)
    return image


@lru_cache(maxsize=32)
def projectile(kind, frame):
    art = pygame.Surface((16, 16), pygame.SRCALPHA)
    if kind == "rock":
        pygame.draw.polygon(art, INK, ((1, 8), (5, 2), (11, 2), (15, 7), (11, 13), (4, 13)))
        pygame.draw.polygon(art, (139, 147, 156), ((3, 8), (6, 4), (10, 4), (13, 7), (10, 11), (5, 11)))
        pygame.draw.rect(art, (190, 201, 193), (6, 5, 4, 2))
    elif kind == "scissors":
        pygame.draw.line(art, INK, (2, 2), (12, 12), 3)
        pygame.draw.line(art, INK, (2, 13), (13, 3), 3)
        pygame.draw.line(art, (212, 222, 220), (6, 9), (12, 3), 2)
        pygame.draw.line(art, (229, 122, 125), (3, 4), (6, 8), 2)
        pygame.draw.line(art, (229, 122, 125), (3, 12), (6, 9), 2)
    else:
        box = (4, 4, 8, 8) if kind == "ball" else (3, 2, 10, 12)
        pygame.draw.rect(art, (104, 104, 111), box)
        pygame.draw.rect(art, (247, 235, 204), pygame.Rect(box).inflate(-2, -2))
        pygame.draw.line(art, (187, 163, 144), (6, 6), (9, 7), 1)
        pygame.draw.line(art, (187, 163, 144), (6, 9), (9, 8), 1)
    return pygame.transform.scale_by(pygame.transform.rotate(art, frame*45), 2)
