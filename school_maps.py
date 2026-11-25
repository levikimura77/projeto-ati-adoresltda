"""Cenários fixos da escola e suas áreas de colisão."""

import random

import pygame


FURNITURE = (
    (),
    ((50, 235, 105, 130), (1125, 245, 105, 104)),
    ((125, 275, 162, 66), (985, 280, 162, 66), (129, 440, 162, 66), (973, 433, 162, 66)),
    ((120, 286, 212, 83), (950, 286, 212, 83), (120, 487, 212, 63), (950, 487, 212, 63)),
    ((120, 235, 175, 76), (986, 235, 175, 76), (165, 475, 148, 86), (968, 475, 128, 52)),
    ((75, 243, 170, 70), (1026, 236, 167, 70), (168, 470, 142, 66), (917, 470, 142, 66)),
)


CLASSROOM_DESKS = ((112, 150), (320, 150), (850, 150), (1060, 150), (116, 485), (1060, 485))


def build_maps(size):
    builders = (classroom, hallway, cafeteria, auditorium, white_room, courtyard)
    return tuple(builder(pygame.Surface(size).convert()) for builder in builders)


def floor(canvas, edge, wall, light, dark, tile=(80, 48)):
    width, height = canvas.get_size()
    canvas.fill(edge)
    pygame.draw.rect(canvas, wall, (36, 100, width-72, 126))
    pygame.draw.rect(canvas, edge, (36, 209, width-72, 17))
    for row, y in enumerate(range(226, height-38, tile[1])):
        for col, x in enumerate(range(36, width-36, tile[0])):
            box = (x+1, y+1, min(tile[0]-2, width-37-x), min(tile[1]-2, height-39-y))
            pygame.draw.rect(canvas, light if (row+col) % 2 == 0 else dark, box)
            if (row*3+col*11) % 5 < 2:
                x2 = x+10+(row*11+col*9) % max(1, box[2]-18)
                y2 = y+6+(col*7) % max(1, box[3]-10)
                pygame.draw.rect(canvas, dark, (x2, y2, 8, 2))
                pygame.draw.rect(canvas, light, (x2+9, y2+2, 4, 2))
            pygame.draw.line(canvas, dark, (x+2, y+box[3]-1), (x+box[2], y+box[3]-1), 2)


def window(canvas, rect):
    scale = 1 if rect.w < 50 else 3
    pygame.draw.rect(canvas, (35, 60, 79), rect.move(0, scale+1))
    pygame.draw.rect(canvas, (234, 210, 169), rect)
    glass = rect.inflate(-4*scale, -4*scale)
    pygame.draw.rect(canvas, (68, 141, 173), glass)
    pygame.draw.rect(canvas, (122, 197, 207), (glass.x, glass.y, glass.w, glass.h//3))
    for x in range(glass.left+14, glass.right-22, 31):
        pygame.draw.polygon(canvas, (160, 216, 217), ((x, glass.top+2), (x+13, glass.top+2),
                                                     (x-4, glass.bottom-2), (x-11, glass.bottom-2)))
    pygame.draw.line(canvas, (49, 79, 99), (rect.centerx, glass.top), (rect.centerx, glass.bottom), scale)
    pygame.draw.line(canvas, (49, 79, 99), (glass.left, rect.centery), (glass.right, rect.centery), scale)


def classroom(canvas):
    canvas.fill((44, 50, 65))
    pygame.draw.rect(canvas, (82, 119, 126), (36, 98, 1208, 112))
    for row, y in enumerate(range(208, 683, 21)):
        color = ((148, 108, 79), (159, 116, 82), (145, 103, 76))[row % 3]
        pygame.draw.rect(canvas, color, (36, y, 1208, 20))
        for x in range(38+(row % 3)*46, 1244, 136):
            pygame.draw.rect(canvas, (111, 78, 64), (x, y+2, 2, 16))
            pygame.draw.rect(canvas, (173, 129, 90), (x+5, y+12, min(20, 1244-x-5), 2))
    pygame.draw.rect(canvas, (65, 69, 76), (405, 117, 470, 83))
    pygame.draw.rect(canvas, (43, 83, 80), (413, 124, 454, 64))
    for i, width in enumerate((173, 122, 152)):
        pygame.draw.rect(canvas, (122, 163, 146), (455, 136+i*13, width, 2))
    pygame.draw.rect(canvas, (197, 157, 108), (409, 186, 461, 8))
    for x in (185, 900):
        window(canvas, pygame.Rect(x, 111, 155, 70))
    for x, y in CLASSROOM_DESKS:
        pygame.draw.ellipse(canvas, (107, 78, 69), (x+9, y+31, 96, 37))
        pygame.draw.rect(canvas, (63, 52, 61), (x+13, y+7, 86, 45))
        pygame.draw.rect(canvas, (193, 143, 94), (x+17, y+9, 78, 29))
        pygame.draw.rect(canvas, (132, 89, 65), (x+17, y+37, 78, 11))
        pygame.draw.rect(canvas, (227, 194, 133), (x+21, y+11, 70, 3))
        pygame.draw.rect(canvas, (232, 224, 199), (x+36, y+15, 27, 15))
        pygame.draw.rect(canvas, (102, 129, 153), (x+39, y+17, 17, 2))
    return canvas


def furniture(canvas, room, side, top, detail):
    for box in FURNITURE[room]:
        rect = pygame.Rect(box)
        pygame.draw.rect(canvas, side, rect.move(7, 9), border_radius=4)
        pygame.draw.rect(canvas, side, rect, border_radius=4)
        pygame.draw.rect(canvas, top, rect.inflate(-8, -8), border_radius=3)
        pygame.draw.line(canvas, detail, (rect.left+9, rect.top+9), (rect.right-10, rect.top+9), 3)
        pygame.draw.rect(canvas, side, (rect.x+5, rect.bottom-17, rect.w-10, 12))
        for x in (rect.left+14, rect.right-22):
            pygame.draw.rect(canvas, detail, (x, rect.bottom-13, 8, 3))


def hallway(canvas):
    floor(canvas, (29, 51, 65), (72, 135, 143), (131, 164, 166), (115, 151, 156))
    for x in range(74, 1200, 47):
        if 565 < x < 691:
            continue
        pygame.draw.rect(canvas, (29, 68, 87), (x, 123, 42, 82))
        pygame.draw.rect(canvas, (46, 109, 130), (x+3, 126, 36, 76))
        for y in (137, 143, 178):
            pygame.draw.line(canvas, (94, 164, 178), (x+9, y), (x+23, y), 2)
    pygame.draw.rect(canvas, (34, 54, 71), (595, 120, 80, 94))
    pygame.draw.rect(canvas, (171, 98, 94), (602, 127, 66, 83))
    pygame.draw.rect(canvas, (240, 193, 130), (649, 168, 10, 4))
    for y in (365, 447):
        pygame.draw.line(canvas, (214, 224, 205), (36, y), (1243, y), 4)
    furniture(canvas, 1, (39, 68, 78), (65, 97, 109), (131, 183, 178))
    return canvas


def cafeteria(canvas):
    floor(canvas, (78, 52, 52), (218, 151, 92), (226, 199, 149), (203, 172, 130), (57, 45))
    pygame.draw.rect(canvas, (67, 53, 65), (415, 123, 450, 91))
    pygame.draw.rect(canvas, (117, 82, 75), (428, 130, 424, 61))
    pygame.draw.rect(canvas, (234, 219, 179), (400, 190, 480, 26))
    for x in range(449, 820, 58):
        pygame.draw.rect(canvas, (194, 181, 166), (x, 166, 40, 19))
        pygame.draw.rect(canvas, (139, 153, 104), (x+5, 170, 28, 9))
    for x in (107, 921):
        window(canvas, pygame.Rect(x, 117, 167, 88))
    furniture(canvas, 2, (100, 65, 55), (169, 100, 71), (236, 164, 100))
    for x, y, _, _ in FURNITURE[2]:
        for offset in (32, 111):
            pygame.draw.circle(canvas, (250, 227, 191), (x+offset, y+36), 11, 3)
    return canvas


def auditorium(canvas):
    floor(canvas, (35, 26, 50), (62, 43, 72), (98, 62, 88), (91, 55, 82), (144, 52))
    pygame.draw.rect(canvas, (42, 29, 50), (128, 116, 1024, 117))
    pygame.draw.rect(canvas, (183, 121, 92), (151, 185, 978, 40))
    pygame.draw.rect(canvas, (122, 73, 68), (151, 225, 978, 16))
    for x in list(range(171, 375, 17)) + list(range(900, 1104, 17)):
        pygame.draw.rect(canvas, (150, 49, 87), (x, 113, 15, 91))
        pygame.draw.line(canvas, (191, 67, 104), (x+3, 116), (x+3, 188), 2)
    pygame.draw.rect(canvas, (132, 75, 96), (510, 250, 260, 430))
    for x in (518, 757):
        pygame.draw.line(canvas, (177, 109, 119), (x, 251), (x, 674), 3)
    for x in range(414, 879, 58):
        pygame.draw.rect(canvas, (223, 159, 105), (x, 193, 23, 3))
        pygame.draw.rect(canvas, (250, 203, 126), (x+9, 187, 4, 5))
    for x, y, w, h in FURNITURE[3]:
        for chair in range(x, x+w, 42):
            pygame.draw.rect(canvas, (52, 28, 53), (chair, y, 36, h), border_radius=5)
            pygame.draw.rect(canvas, (178, 68, 105), (chair+3, y+4, 30, 29), border_radius=4)
            pygame.draw.rect(canvas, (128, 52, 90), (chair+3, y+h-19, 30, 14), border_radius=4)
    return canvas


def white_room(canvas):
    floor(canvas, (64, 82, 112), (194, 213, 228), (182, 201, 216), (169, 189, 208), (112, 57))
    pygame.draw.rect(canvas, (87, 112, 146), (373, 119, 534, 93))
    pygame.draw.rect(canvas, (236, 244, 246), (380, 126, 520, 79))
    for x in range(393, 887, 97):
        pygame.draw.rect(canvas, (132, 164, 188), (x, 138, 80, 8))
        for y in (157, 171, 185):
            pygame.draw.rect(canvas, (186, 206, 221), (x, y, 72, 5))
    for x in (129, 948):
        window(canvas, pygame.Rect(x, 123, 181, 78))
    pygame.draw.rect(canvas, (142, 166, 199), (472, 263, 336, 350), 4)
    pygame.draw.circle(canvas, (141, 164, 198), (640, 435), 68, 3)
    furniture(canvas, 4, (85, 107, 138), (211, 221, 231), (250, 252, 253))
    return canvas


def campus(size):
    art = pygame.Surface((320, 180)).convert()
    rng = random.Random(47)
    for y in range(126):
        pygame.draw.line(art, (81+y//2, 158+y//3, 198+y//4), (0, y), (319, y))
    for x, y, width in ((19, 28, 56), (116, 14, 58), (213, 31, 59), (278, 12, 44)):
        pygame.draw.rect(art, (176, 218, 225), (x, y+8, width, 8))
        for dx, dy, w in ((6, 4, 14), (15, 0, 18), (31, 5, 17)):
            pygame.draw.rect(art, (235, 241, 224), (x+dx, y+dy, w, 12))
    pygame.draw.rect(art, (54, 107, 124), (34, 69, 83, 55))
    pygame.draw.rect(art, (122, 177, 177), (38, 65, 79, 12))
    pygame.draw.rect(art, (117, 73, 72), (117, 57, 191, 76))
    pygame.draw.rect(art, (194, 117, 86), (117, 59, 191, 66))
    pygame.draw.rect(art, (244, 164, 112), (113, 56, 195, 6))
    for y in range(66, 126, 5):
        pygame.draw.line(art, (173, 104, 85), (120, y), (306, y))
        for x in range(129+(y % 3)*5, 306, 19):
            pygame.draw.line(art, (173, 104, 85), (x, y), (x, y+4))
    for y in (72, 94):
        for x in range(130, 277, 25):
            window(art, pygame.Rect(x, y, 24, 18))
    pygame.draw.rect(art, (46, 79, 98), (279, 91, 19, 35))
    pygame.draw.rect(art, (114, 178, 185), (282, 93, 12, 24))
    pygame.draw.rect(art, (228, 182, 131), (278, 125, 23, 4))
    pygame.draw.rect(art, (125, 156, 104), (0, 124, 320, 7))
    pygame.draw.rect(art, (203, 191, 162), (0, 131, 320, 49))
    for y in (134, 141, 153, 169):
        pygame.draw.line(art, (149, 145, 142), (0, y), (319, y))
    for x in range(-180, 500, 48):
        pygame.draw.line(art, (149, 145, 142), (160+(x-160)//4, 131), (x, 179))
    for x, y, r in ((16, 102, 26), (66, 105, 17), (102, 98, 22), (307, 92, 24)):
        pygame.draw.rect(art, (92, 73, 72), (x-3, y-7, 6, 33))
        pygame.draw.rect(art, (155, 102, 74), (x, y-6, 2, 30))
        for level, color in enumerate(((48, 91, 89), (53, 121, 99), (87, 151, 105), (144, 176, 114))):
            for _ in range(30):
                dx, dy = rng.randint(-r, r), rng.randint(-r, r)
                if dx*dx + dy*dy < r*r:
                    pygame.draw.rect(art, color, (x+dx-level*2, y+dy-level*4, rng.randint(4, 11), rng.randint(3, 8)))
    return pygame.transform.scale(art, size)


def courtyard(canvas):
    canvas.blit(campus((1280, 392)), (0, 0))
    pygame.draw.rect(canvas, (112, 144, 107), (0, 243, 1280, 477))
    pygame.draw.rect(canvas, (201, 193, 158), (36, 259, 1208, 424))
    for y in range(260, 684, 47):
        pygame.draw.line(canvas, (166, 160, 141), (36, y), (1243, y), 3)
        for x in range(72+(y % 2)*32, 1243, 83):
            pygame.draw.line(canvas, (171, 165, 144), (x, y), (x, min(y+47, 682)), 2)
    furniture(canvas, 5, (69, 90, 76), (111, 162, 113), (187, 211, 135))
    return canvas
