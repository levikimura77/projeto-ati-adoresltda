"""Atiçadores LTDA — jogo 2D feito em Python com Pygame.

Execute com: python main.py (requer pygame-ce ou pygame).
"""
from __future__ import annotations

import json
import math
import random
import sys
from array import array
from pathlib import Path

import pygame

ROOT = Path(__file__).resolve().parent
W, H = 1280, 720
FPS = 60
WHITE = (245, 245, 245)
GOLD = (255, 225, 76)
CYAN = (125, 220, 255)
BG = (10, 14, 40)


def asset(*parts: str) -> Path:
    return ROOT.joinpath(*parts)


def load_image(path: Path):
    try:
        return pygame.image.load(str(path)).convert_alpha()
    except (pygame.error, FileNotFoundError):
        return None


class Game:
    CLASSROOM_DESKS = ((112, 150), (320, 150), (850, 150), (1060, 150), (116, 485), (1060, 485))
    DIFFICULTIES = {
        "easy": {"hp": 200, "speed": 65, "interval": 1.8, "damage": 10, "rps_interval": None, "rps_speed": 0, "rps_damage": 0},
        "medium": {"hp": 230, "speed": 78, "interval": 1.55, "damage": 12, "rps_interval": None, "rps_speed": 0, "rps_damage": 0},
        "hard": {"hp": 260, "speed": 92, "interval": 1.25, "damage": 14, "rps_interval": 4.2, "rps_speed": 245, "rps_damage": 14},
        "impossible": {"hp": 400, "speed": 180, "interval": .72, "damage": 20, "rps_interval": 2.5, "rps_speed": 340, "rps_damage": 18},
    }
    DIFFICULTY_ORDER = ("easy", "medium", "hard", "impossible")

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Atiçadores LTDA — O Jogo")
        self.screen = pygame.display.set_mode((W, H), pygame.RESIZABLE)
        self.canvas = pygame.Surface((W, H))
        self.clock = pygame.time.Clock()
        self.fonts = {}
        self.images = {}
        self.load_assets()
        self.state = "loading"
        self.paused = False
        self.settings_return_to_pause = False
        self.saved_prompt = False
        self.state_time = 0.0
        self.progress = 0.0
        self.load_tick = 0.0
        self.loading_step = 0
        self.name = "Jogador"
        self.gender = "boy"
        self.difficulty = "easy"
        self.settings = {"brightness": .7, "master": .8, "sfx": .8,
                         "music": .6, "fullscreen": False, "language": "pt_BR"}
        self.settings_draft = self.settings.copy()
        self.read_settings()
        self.init_audio()
        if self.settings["fullscreen"]:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.controls = []
        self.dialogue_step = 0
        self.phase = "intro"
        self.player = pygame.Vector2(640, 540)
        self.boss = pygame.Vector2(640, 160)
        self.player_hp_max = 5
        self.player_hp, self.boss_hp = self.player_hp_max, 200
        self.boss_hp_max = 200
        self.direction = pygame.Vector2(0, 1)
        self.boss_direction = pygame.Vector2(0, 1)
        self.player_moving = False
        self.walk_anim_time = 0.0
        self.boss_moving = False
        self.boss_anim_time = 0.0
        self.attack_timer = self.boss_attack_timer = 0.0
        self.attack_flash = 0.0
        self.player_action = "idle"
        self.player_action_time = 0.0
        self.player_action_hit = False
        self.player_action_direction = self.direction.copy()
        self.player_hurt_timer = 0.0
        self.boss_action = "idle"
        self.boss_action_time = 0.0
        self.boss_action_hit = False
        self.boss_hurt_timer = 0.0
        self.impact_timer = 0.0
        self.impact_position = pygame.Vector2(0, 0)
        self.player_blocking = False
        self.block_keys_down = set()
        self.block_press_consumed = False
        self.block_flash = 0.0
        self.rps_attack_timer = 0.0
        self.projectiles = []
        self.paper_projectiles = []
        self.paper_cooldown = 0.0
        self.feedback = ""
        self.feedback_time = 0.0
        self.name_edit = ""
        self.char_index = 0
        self.credits = False
        self.slider_drag = None
        self.save_path = Path.home() / ".aticadores_save.json"

    def load_assets(self):
        names = {
            "loading_logo": ("assets", "ui", "logo.png"),
            "menu_bg": ("assets", "ui", "ChatGPT Image 19 de ago. de 2026, 12_50_59.png"),
            "select_bg": ("assets", "ui", "ChatGPT Image 19 de ago. de 2026, 12_50_59.png"),
            "button_normal": ("assets", "ui", "sheetbotao.png"),
            "button_pressed": ("assets", "ui", "ChatGPT Image 19 de ago. de 2026, 14_31_39.png"),
            "button_hover": ("assets", "ui", "ChatGPT Image 19 de ago. de 2026, 14_30_45.png"),
            "boy": ("assets", "ui", "mininu.png"),
            "girl": ("assets", "ui", "minina.png"),
            "professor": ("assets", "ui", "professo.png"),
        }
        self.images = {k: load_image(asset(*p)) for k, p in names.items()}
        self.player_frames = {}
        self.player_punch_frames = {}
        self.player_hurt_frames = {}
        self.player_block_frames = {}
        for gender in ("boy", "girl"):
            self.player_frames[gender] = {
                "idle_down": [self.make_player_sprite(gender, "down", 0)],
                "idle_up": [self.make_player_sprite(gender, "up", 0)],
                "idle_side": [self.make_player_sprite(gender, "side", 0)],
                "walk_down": [self.make_player_sprite(gender, "down", 0), self.make_player_sprite(gender, "down", 1)],
                "walk_up": [self.make_player_sprite(gender, "up", 0), self.make_player_sprite(gender, "up", 1)],
                "walk_right": [self.make_player_sprite(gender, "side", 0), self.make_player_sprite(gender, "side", 1)],
                "walk_left": [pygame.transform.flip(self.make_player_sprite(gender, "side", 0), True, False),
                              pygame.transform.flip(self.make_player_sprite(gender, "side", 1), True, False)],
            }
            self.player_punch_frames[gender] = {
                facing: [self.make_player_sprite(gender, facing, 0, "punch"),
                         self.make_player_sprite(gender, facing, 1, "punch")]
                for facing in ("down", "up", "side")
            }
            self.player_hurt_frames[gender] = {
                facing: self.make_player_sprite(gender, facing, 0, "hurt")
                for facing in ("down", "up", "side")
            }
            self.player_block_frames[gender] = {
                facing: self.make_player_sprite(gender, facing, 0, "block")
                for facing in ("down", "up", "side")
            }
        self.menu_buttons = self.load_menu_buttons()
        self.boss_sprites = [self.make_boss_sprite(0), self.make_boss_sprite(1)]
        self.boss_attack_sprites = [self.make_boss_sprite(0, "attack"), self.make_boss_sprite(1, "attack")]
        self.boss_hurt_sprites = [self.make_boss_sprite(0, "hurt"), self.make_boss_sprite(1, "hurt")]

    def load_menu_buttons(self):
        regions = [
            (311, 10, 925, 284, 270, 0, 1036, 304, 279, 11, 1007, 285),
            (308, 275, 931, 263, 270, 270, 1020, 278, 276, 270, 1003, 276),
            (314, 523, 901, 255, 272, 523, 996, 252, 275, 522, 983, 258),
            (321, 780, 894, 230, 279, 775, 986, 241, 289, 779, 966, 232),
        ]
        normal, pressed, hover = (self.images.get(k) for k in ("button_normal", "button_pressed", "button_hover"))
        buttons = []
        for r in regions:
            sprites = []
            for image, offset in ((normal, 0), (pressed, 4), (hover, 8)):
                if not image:
                    sprites.append(None)
                    continue
                x, y, w, h = r[offset:offset+4]
                x, y = max(0, x), max(0, y)
                w, h = min(w, image.get_width()-x), min(h, image.get_height()-y)
                sprites.append(image.subsurface((x, y, w, h)).copy() if w > 0 and h > 0 else None)
            buttons.append(sprites)
        return buttons

    def font(self, size):
        if size not in self.fonts:
            self.fonts[size] = pygame.font.SysFont("arial", size, bold=False)
        return self.fonts[size]

    def tx(self, portuguese, english):
        values = self.settings_draft if getattr(self, "state", "") == "settings" else self.settings
        return english if values.get("language") == "en" else portuguese

    def difficulty_profile(self):
        return self.DIFFICULTIES.get(self.difficulty, self.DIFFICULTIES["easy"])

    def player_hearts_for_difficulty(self):
        return 5 if self.difficulty in ("easy", "medium") else 3

    def blocking_available(self):
        return self.difficulty in ("hard", "impossible")

    def difficulty_name(self, difficulty=None):
        key = difficulty or self.difficulty
        names = {
            "easy": self.tx("FÁCIL", "EASY"),
            "medium": self.tx("MÉDIO", "MEDIUM"),
            "hard": self.tx("DIFÍCIL", "HARD"),
            "impossible": self.tx("IMPOSSÍVEL", "IMPOSSIBLE"),
        }
        return names.get(key, names["easy"])

    def init_audio(self):
        self.audio_ok = False
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            pygame.mixer.set_num_channels(8)
            self.music_channel = pygame.mixer.Channel(0)
            self.sfx_channel = pygame.mixer.Channel(1)
            self.music_sound = pygame.mixer.Sound(buffer=self.make_chiptune().tobytes())
            self.fight_music_sound = pygame.mixer.Sound(buffer=self.make_chiptune(fast=True).tobytes())
            self.death_music_sound = pygame.mixer.Sound(buffer=self.make_chiptune(sad=True).tobytes())
            self.victory_sound = pygame.mixer.Sound(buffer=self.make_victory_sound().tobytes())
            self.click_sound = pygame.mixer.Sound(buffer=self.make_tone((660,), .045, 5500, fade=True).tobytes())
            self.punch_sound = pygame.mixer.Sound(buffer=self.make_tone((125, 82), .12, 8500, fade=True).tobytes())
            self.hit_sound = pygame.mixer.Sound(buffer=self.make_tone((72, 108, 145), .18, 7600, fade=True).tobytes())
            self.block_sound = pygame.mixer.Sound(buffer=self.make_tone((310, 470), .09, 6500, fade=True).tobytes())
            self.audio_ok = True
            self.current_music = None
            self.set_music()
            self.apply_audio(self.settings)
        except pygame.error:
            # Alguns dispositivos sem saída de áudio podem executar o jogo normalmente.
            self.audio_ok = False

    @staticmethod
    def make_tone(frequencies, duration, amplitude, fade=False):
        rate = 22050
        samples = array("h")
        count = int(rate * duration)
        for i in range(count):
            envelope = max(0.0, 1.0 - i/count) if fade else 1.0
            value = sum(math.sin(2*math.pi*frequency*i/rate) for frequency in frequencies) / len(frequencies)
            sample = int(amplitude * envelope * value)
            samples.extend((sample, sample))
        return samples

    @staticmethod
    def make_victory_sound():
        """Pequeno arpejo ascendente em chiptune para marcar a vitória."""
        rate, note_duration = 22050, .14
        notes = (523.25, 659.25, 783.99, 1046.5, 783.99, 1046.5)
        samples = array("h")
        for i in range(int(rate*note_duration*len(notes))):
            t = i/rate
            index = min(len(notes)-1, int(t/note_duration))
            local = t-index*note_duration
            phase = (local*notes[index]) % 1.0
            wave = 1.0-4.0*abs(phase-.5)
            envelope = min(1.0, local/.008) * max(0.0, 1.0-local/note_duration)
            sample = int(wave*envelope*6200)
            samples.extend((sample, sample))
        return samples

    @staticmethod
    def make_chiptune(sad=False, fast=False):
        """Tema original em pulso/bass/chiptune com bateria simples, em loop de 4 compassos."""
        bpm = 72 if sad else 108 if fast else 78
        rate, beat_seconds = 22050, 60.0/bpm
        eighth = beat_seconds / 2
        # A variação de derrota usa a mesma paleta, em menor e com pulso mais lento.
        if sad:
            melody = [57,60,64,60, 57,60,65,60, 55,60,64,60, 55,59,62,59,
                      57,60,64,67, 65,64,60,57, 53,57,60,57, 55,59,62,57]
            roots = [45, 41, 48, 43]  # Am, F, C, G
        elif fast:
            melody = [72,76,79,76, 74,77,81,77, 72,76,79,84, 81,79,76,72,
                      72,76,79,84, 83,81,79,76, 74,77,81,86, 84,81,79,72]
            roots = [48, 45, 41, 43]  # C, Am, F, G
        else:
            melody = [64,67,72,67, 69,67,64,60, 62,64,67,69, 72,69,67,64,
                      64,67,72,76, 74,72,69,67, 69,72,76,74, 72,69,67,60]
            roots = [48, 43, 45, 41]  # C, G, Am, F
        count = int(rate * beat_seconds * 16)
        samples = array("h")
        for i in range(count):
            t = i / rate
            beat = int(t / beat_seconds) % 16
            eighth_index = int(t / eighth) % len(melody)
            note = melody[eighth_index]
            note_start = eighth_index * eighth
            local_note = t - note_start
            melody_freq = 440.0 * (2.0 ** ((note-69)/12.0))
            phase = (t * melody_freq) % 1.0
            lead_wave = 1.0 - 4.0*abs(phase-.5)
            note_env = min(1.0, local_note/.008) * max(0.0, 1.0-local_note/(eighth*1.05))
            melody_sample = lead_wave * note_env * (3400 if sad else 4700)

            root = roots[(beat // 4) % len(roots)]
            bass_note = root if beat % 4 in (0, 2) else root + 7
            bass_freq = 440.0 * (2.0 ** ((bass_note-69)/12.0))
            bass_phase = (t*bass_freq) % 1.0
            bass_triangle = 1.0 - 4.0*abs(bass_phase-.5)
            bass_sample = bass_triangle * (2400 if sad else 3000)

            # Bumbo nos tempos fortes, caixa nos tempos 2 e 4 e chimbal nos contratempos.
            within_beat = t % beat_seconds
            drum = 0.0
            if beat % 4 in (0, 2) and within_beat < .16:
                kick_env = math.exp(-within_beat*24)
                drum += math.sin(2*math.pi*(65+45*math.exp(-within_beat*24))*within_beat) * kick_env * (2300 if sad else 3900)
            if not sad and beat % 4 in (1, 3) and within_beat < .12:
                snare_env = math.exp(-within_beat*28)
                noise = math.sin(i*1.731) * .65 + math.sin(i*.417) * .35
                drum += (noise + .25*math.sin(2*math.pi*150*within_beat))*snare_env*1650
            if not sad and int(t/eighth) % 2 == 1 and t % eighth < .035:
                hat_env = math.exp(-(t%eighth)*95)
                drum += math.sin(i*2.41)*hat_env*320

            sample = max(-26000, min(26000, int(melody_sample+bass_sample+drum)))
            samples.extend((sample, sample))
        return samples

    def apply_audio(self, settings):
        if self.audio_ok:
            master = float(settings["master"])
            self.music_channel.set_volume(master * float(settings["music"]))
            self.sfx_channel.set_volume(master * float(settings["sfx"]))

    def set_music(self, sad=False, fast=False):
        if not self.audio_ok:
            return
        sound = self.death_music_sound if sad else self.fight_music_sound if fast else self.music_sound
        if self.current_music is sound and self.music_channel.get_busy():
            return
        self.music_channel.stop()
        self.music_channel.play(sound, loops=-1)
        self.current_music = sound

    def play_sfx(self, name="click"):
        if self.audio_ok:
            sound = {"punch": self.punch_sound, "hit": self.hit_sound,
                     "block": self.block_sound, "victory": self.victory_sound}.get(name, self.click_sound)
            self.sfx_channel.play(sound)

    def text(self, text, pos, size=22, color=WHITE, center=False):
        surf = self.font(size).render(str(text), True, color)
        rect = surf.get_rect()
        if center:
            rect.center = pos
        else:
            rect.topleft = pos
        self.canvas.blit(surf, rect)
        return rect

    def wrapped(self, text, rect, size=20, color=WHITE, line_gap=5):
        y = rect.top
        for paragraph in text.split("\n"):
            words, line = paragraph.split(" "), ""
            for word in words:
                candidate = (line + " " + word).strip()
                if self.font(size).size(candidate)[0] > rect.width and line:
                    self.text(line, (rect.left, y), size, color)
                    y += size + line_gap
                    line = word
                else:
                    line = candidate
            self.text(line, (rect.left, y), size, color)
            y += size + line_gap

    def image_fit(self, key, rect, alpha=255):
        img = self.images.get(key)
        if img:
            fitted = pygame.transform.smoothscale(img, rect.size)
            if alpha != 255:
                fitted.set_alpha(alpha)
            self.canvas.blit(fitted, rect)

    def image_contain(self, key, rect):
        img = self.images.get(key)
        if img:
            scale = min(rect.width / img.get_width(), rect.height / img.get_height())
            size = (max(1, round(img.get_width()*scale)), max(1, round(img.get_height()*scale)))
            fitted = pygame.transform.scale(img, size)
            self.canvas.blit(fitted, fitted.get_rect(center=rect.center))

    def make_player_sprite(self, gender="boy", facing="down", step=0, action="walk"):
        """Sprite limpo em pixel art inspirado no retrato da seleção de personagem."""
        s = pygame.Surface((40, 64), pygame.SRCALPHA)
        ink = (20, 18, 31)
        hair = (19, 20, 34) if gender == "boy" else (31, 24, 43)
        skin, red, blue = (246, 166, 99), (178, 30, 74), (48, 83, 190)
        pants = (39, 40, 57) if gender == "boy" else (75, 56, 127)
        shoes = (118, 121, 143) if gender == "boy" else (232, 232, 242)

        # Passos alternados: braços balançam em oposição às pernas.
        left_leg = -3 if step else 2
        right_leg = 2 if step else -3
        arm_swing = 2 if step else -1
        if facing == "side":
            pygame.draw.rect(s, ink, (8, 25+arm_swing, 8, 17))
            pygame.draw.rect(s, red, (9, 26+arm_swing, 6, 11))
            pygame.draw.rect(s, ink, (27, 23-arm_swing, 7, 17))
            pygame.draw.rect(s, skin, (28, 32-arm_swing, 5, 9))
        else:
            pygame.draw.rect(s, ink, (4, 25+arm_swing, 8, 17))
            pygame.draw.rect(s, red, (5, 26+arm_swing, 6, 11))
            pygame.draw.rect(s, skin, (5, 35+arm_swing, 6, 9))
            pygame.draw.rect(s, ink, (28, 25-arm_swing, 8, 17))
            pygame.draw.rect(s, red, (29, 26-arm_swing, 6, 11))
            pygame.draw.rect(s, skin, (29, 35-arm_swing, 6, 9))

        # Calça e tênis; o contorno acompanha o movimento sem deixar rastros.
        for x, offset in ((12, left_leg), (22, right_leg)):
            pygame.draw.rect(s, ink, (x+offset, 42, 9, 16))
            pygame.draw.rect(s, pants, (x+offset+1, 43, 7, 13))
            pygame.draw.rect(s, ink, (x+offset-2, 55, 13, 7))
            pygame.draw.rect(s, shoes, (x+offset-1, 56, 11, 4))

        # Camiseta vinho e avental/colete azul como no modelo da seleção.
        pygame.draw.rect(s, ink, (7, 20, 27, 26))
        pygame.draw.rect(s, red, (8, 21, 25, 24))
        pygame.draw.rect(s, red, (5, 27, 30, 7))
        pygame.draw.rect(s, ink, (11, 24, 18, 22))
        pygame.draw.rect(s, blue, (12, 25, 16, 19))
        pygame.draw.rect(s, (31, 55, 132), (14, 30, 4, 4))
        pygame.draw.rect(s, (248, 244, 224), (19, 25, 3, 6))
        pygame.draw.rect(s, (232, 47, 57), (19, 30, 3, 4))
        pygame.draw.rect(s, (235, 235, 246), (12, 40, 5, 2))
        pygame.draw.rect(s, (235, 235, 246), (18, 42, 5, 2))
        pygame.draw.rect(s, (235, 235, 246), (24, 40, 4, 2))

        # Cabeça e cabelo; ao caminhar para cima mostramos a parte de trás.
        if facing == "up":
            pygame.draw.rect(s, ink, (8, 4, 24, 22))
            pygame.draw.rect(s, hair, (10, 4, 20, 17))
            pygame.draw.rect(s, hair, (7, 9, 26, 8))
        else:
            pygame.draw.rect(s, ink, (9, 4, 22, 23))
            pygame.draw.rect(s, skin, (11, 9, 18, 16))
            pygame.draw.rect(s, skin, (9, 14, 22, 8))
            pygame.draw.rect(s, hair, (10, 4, 20, 9))
            pygame.draw.rect(s, hair, (7, 8, 5, 12))
            pygame.draw.rect(s, hair, (28, 8, 5, 12))
            pygame.draw.rect(s, hair, (11, 2, 6, 4))
            pygame.draw.rect(s, hair, (17, 1, 7, 5))
            pygame.draw.rect(s, hair, (24, 3, 6, 4))
            if facing == "side":
                pygame.draw.rect(s, skin, (28, 15, 4, 3))
                pygame.draw.rect(s, ink, (23, 13, 3, 3))
                pygame.draw.rect(s, hair, (8, 8, 7, 12))
            else:
                pygame.draw.rect(s, ink, (14, 14, 3, 3))
                pygame.draw.rect(s, ink, (23, 14, 3, 3))
                pygame.draw.rect(s, (98, 43, 40), (18, 21, 5, 2))
        if action == "punch":
            if facing == "down":
                pygame.draw.rect(s, ink, (17, 35, 7, 15))
                pygame.draw.rect(s, red, (18, 36, 5, 7))
                pygame.draw.rect(s, skin, (17, 43, 7, 7))
            elif facing == "up":
                pygame.draw.rect(s, ink, (17, 17, 7, 14))
                pygame.draw.rect(s, red, (18, 23, 5, 6))
                pygame.draw.rect(s, skin, (17, 17, 7, 7))
            else:
                pygame.draw.rect(s, ink, (25, 28, 14, 7))
                pygame.draw.rect(s, red, (29, 29, 6, 5))
                pygame.draw.rect(s, skin, (35, 28, 5, 7))
        elif action == "hurt":
            pygame.draw.rect(s, ink, (5, 14, 7, 12))
            pygame.draw.rect(s, skin, (6, 13, 6, 7))
            pygame.draw.rect(s, ink, (28, 14, 7, 12))
            pygame.draw.rect(s, skin, (28, 13, 6, 7))
        elif action == "block":
            if facing == "side":
                pygame.draw.rect(s, ink, (24, 18, 8, 17))
                pygame.draw.rect(s, red, (25, 20, 6, 9))
                pygame.draw.rect(s, skin, (24, 17, 8, 6))
            else:
                pygame.draw.rect(s, ink, (8, 18, 8, 17))
                pygame.draw.rect(s, red, (9, 20, 6, 9))
                pygame.draw.rect(s, skin, (8, 17, 8, 6))
                pygame.draw.rect(s, ink, (24, 18, 8, 17))
                pygame.draw.rect(s, red, (25, 20, 6, 9))
                pygame.draw.rect(s, skin, (24, 17, 8, 6))
        return s

    def make_boss_sprite(self, step=0, action="walk"):
        """Desenha um sprite original em pixel art numa tela pequena e transparente."""
        s = pygame.Surface((48, 64), pygame.SRCALPHA)
        outline, hair = (24, 19, 28), (49, 30, 25)
        skin, shirt, red, pants = (235, 153, 91), (47, 62, 105), (148, 28, 43), (35, 39, 54)
        # sapatos e pernas
        if step:
            pygame.draw.rect(s, outline, (5, 54, 15, 7)); pygame.draw.rect(s, outline, (30, 51, 14, 7))
            pygame.draw.rect(s, pants, (9, 40, 10, 16)); pygame.draw.rect(s, pants, (29, 37, 10, 16))
            pygame.draw.rect(s, (100, 105, 119), (4, 58, 17, 4)); pygame.draw.rect(s, (100, 105, 119), (29, 55, 16, 4))
        else:
            pygame.draw.rect(s, outline, (9, 54, 13, 7)); pygame.draw.rect(s, outline, (27, 54, 13, 7))
            pygame.draw.rect(s, pants, (12, 39, 10, 17)); pygame.draw.rect(s, pants, (27, 39, 10, 17))
            pygame.draw.rect(s, (100, 105, 119), (8, 58, 16, 4)); pygame.draw.rect(s, (100, 105, 119), (26, 58, 16, 4))
        # tronco, paletó e camisa
        pygame.draw.rect(s, outline, (8, 21, 32, 23))
        pygame.draw.rect(s, red, (10, 22, 28, 21)); pygame.draw.rect(s, shirt, (19, 22, 10, 19))
        pygame.draw.rect(s, (225, 194, 108), (22, 24, 3, 14))
        # braços e punhos
        pygame.draw.rect(s, outline, (4, 24, 8, 22)); pygame.draw.rect(s, red, (5, 25, 6, 16))
        pygame.draw.rect(s, skin, (5, 40, 7, 8)); pygame.draw.rect(s, outline, (36, 24, 8, 22))
        pygame.draw.rect(s, red, (37, 25, 6, 16)); pygame.draw.rect(s, skin, (37, 40, 7, 8))
        if action == "attack":
            pygame.draw.rect(s, outline, (31, 25, 15, 8))
            pygame.draw.rect(s, red, (34, 26, 10, 6))
            pygame.draw.rect(s, skin, (42, 25, 6, 8))
        elif action == "hurt":
            pygame.draw.rect(s, skin, (4, 33, 7, 8))
            pygame.draw.rect(s, skin, (37, 33, 7, 8))
        # cabeça, cabelo e expressão
        pygame.draw.rect(s, outline, (12, 7, 24, 19)); pygame.draw.rect(s, skin, (14, 11, 20, 15))
        pygame.draw.rect(s, hair, (11, 6, 26, 8)); pygame.draw.rect(s, hair, (9, 10, 6, 9))
        pygame.draw.rect(s, hair, (14, 4, 6, 5)); pygame.draw.rect(s, hair, (23, 3, 7, 6))
        pygame.draw.rect(s, hair, (32, 7, 6, 8)); pygame.draw.rect(s, outline, (17, 15, 4, 3))
        pygame.draw.rect(s, outline, (27, 15, 4, 3)); pygame.draw.rect(s, (100, 38, 35), (21, 21, 7, 2))
        # faixa de chefe e medalha
        pygame.draw.rect(s, (205, 42, 45), (11, 32, 26, 4)); pygame.draw.rect(s, GOLD, (31, 27, 4, 4))
        return s

    def panel(self, rect, color=(18, 24, 52, 235), border=CYAN, radius=12):
        surf = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(surf, color, surf.get_rect(), border_radius=radius)
        pygame.draw.rect(surf, border, surf.get_rect(), 2, border_radius=radius)
        self.canvas.blit(surf, rect)

    def button(self, key, label, rect, *, font=22):
        mouse = pygame.mouse.get_pos()
        scale = pygame.Vector2(self.screen.get_size())
        mouse = (mouse[0] * W / max(scale.x, 1), mouse[1] * H / max(scale.y, 1))
        hovered = rect.collidepoint(mouse)
        color = (48, 94, 132) if hovered else (28, 55, 88)
        pygame.draw.rect(self.canvas, color, rect, border_radius=8)
        pygame.draw.rect(self.canvas, GOLD if hovered else CYAN, rect, 2, border_radius=8)
        self.text(label, rect.center, font, WHITE, True)
        self.controls.append((key, rect))

    def bg_image(self, key, overlay=0):
        self.image_fit(key, pygame.Rect(0, 0, W, H))
        if overlay:
            pygame.draw.rect(self.canvas, (0, 0, 0, overlay), (0, 0, W, H))

    def read_settings(self):
        try:
            data = json.loads((Path.home() / ".aticadores_settings.json").read_text(encoding="utf-8"))
            self.settings.update(data)
        except (OSError, ValueError):
            pass

    def save_settings(self):
        try:
            (Path.home() / ".aticadores_settings.json").write_text(
                json.dumps(self.settings, ensure_ascii=False, indent=2), encoding="utf-8")
        except OSError:
            self.feedback = "Não foi possível salvar as configurações."

    def set_state(self, state):
        self.state, self.state_time = state, 0.0

    def save_game(self):
        if self.phase not in ("intro", "combat"):
            return False
        data = {
            "name": self.name, "gender": self.gender, "player_hp": self.player_hp,
            "difficulty": self.difficulty,
            "boss_hp": self.boss_hp, "player": [self.player.x, self.player.y],
            "boss": [self.boss.x, self.boss.y], "phase": self.phase,
            "dialogue_step": self.dialogue_step,
        }
        try:
            self.save_path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            self.save_settings()
            return True
        except OSError:
            return False

    def load_game(self):
        try:
            data = json.loads(self.save_path.read_text(encoding="utf-8"))
            self.name = str(data.get("name", "Jogador"))
            self.gender = data.get("gender", "boy") if data.get("gender") in ("boy", "girl") else "boy"
            self.difficulty = data.get("difficulty", "easy") if data.get("difficulty") in self.DIFFICULTIES else "easy"
            self.boss_hp_max = self.difficulty_profile()["hp"]
            self.player_hp_max = self.player_hearts_for_difficulty()
            saved_player_hp = int(data.get("player_hp", self.player_hp_max))
            # Converte saves antigos que guardavam vida de 0 a 100 para corações.
            if saved_player_hp > self.player_hp_max:
                saved_player_hp = math.ceil(saved_player_hp / 100 * self.player_hp_max)
            self.player_hp = max(1, min(self.player_hp_max, saved_player_hp))
            self.boss_hp = max(1, min(self.boss_hp_max, int(data.get("boss_hp", self.boss_hp_max))))
            self.player.update(*data.get("player", [640, 540]))
            self.boss.update(*data.get("boss", [640, 160]))
            self.phase = data.get("phase", "combat") if data.get("phase") in ("intro", "combat") else "combat"
            self.dialogue_step = max(0, min(4, int(data.get("dialogue_step", 4))))
            if self.phase == "intro" and self.dialogue_step >= 4:
                self.phase = "combat"
            self.paused = False
            self.saved_prompt = False
            self.player_action = self.boss_action = "idle"
            self.player_hurt_timer = self.boss_hurt_timer = self.impact_timer = 0.0
            self.player_moving = self.boss_moving = False
            self.walk_anim_time = self.boss_anim_time = 0.0
            self.attack_timer = self.boss_attack_timer = 0.0
            self.rps_attack_timer = 0.0
            self.projectiles.clear()
            self.paper_projectiles.clear()
            self.paper_cooldown = 0.0
            self.player_blocking = False
            self.block_keys_down.clear()
            self.block_press_consumed = False
            self.set_state("game")
            self.set_music(fast=self.phase == "combat")
            return True
        except (OSError, ValueError, TypeError, json.JSONDecodeError):
            return False

    def start_game(self):
        self.set_music()
        self.player.update(640, 540)
        self.boss.update(640, 160)
        self.direction.update(0, 1)
        self.player_action_direction.update(0, 1)
        self.player_moving = self.boss_moving = False
        self.walk_anim_time = self.boss_anim_time = 0.0
        self.player_hp_max = self.player_hearts_for_difficulty()
        self.player_hp = self.player_hp_max
        self.boss_hp_max = self.difficulty_profile()["hp"]
        self.boss_hp = self.boss_hp_max
        self.player_action = self.boss_action = "idle"
        self.player_hurt_timer = self.boss_hurt_timer = 0.0
        self.player_action_time = self.boss_action_time = 0.0
        self.player_action_hit = self.boss_action_hit = False
        self.boss_direction.update(0, 1)
        self.impact_timer = 0.0
        self.player_blocking = False
        self.block_keys_down.clear()
        self.block_press_consumed = False
        self.block_flash = 0.0
        self.rps_attack_timer = 0.0
        self.projectiles.clear()
        self.paper_projectiles.clear()
        self.paper_cooldown = 0.0
        self.paused = False
        self.dialogue_step, self.phase = 0, "intro"
        self.attack_timer = self.boss_attack_timer = 0.0
        self.set_state("game")

    def render_loading(self):
        self.canvas.fill((10, 13, 41))
        self.image_contain("loading_logo", pygame.Rect(390, 50, 500, 280))
        self.text(self.tx("O JOGO", "THE GAME"), (W//2, 330), 24, CYAN, True)
        if self.progress < 100:
            self.load_tick += self.state_time
            if self.load_tick > .04:
                self.progress = min(100, self.progress + random.uniform(2.5, 7))
                self.load_tick = 0.0
        self.state_time = 0.0
        step = min(int(self.progress // 20), 4)
        labels = ["Carregando assets", "Inicializando mundo", "Preparando personagens", "Carregando músicas", "Quase pronto"]
        self.text("Concluído!" if self.progress >= 100 else labels[step], (W//2, 515), 20, (200, 200, 210), True)
        pygame.draw.rect(self.canvas, (35, 40, 65), (340, 550, 600, 28), border_radius=8)
        pygame.draw.rect(self.canvas, CYAN, (340, 550, int(600*self.progress/100), 28), border_radius=8)

    def render_menu(self):
        self.bg_image("menu_bg")
        english = self.settings["language"] == "en"
        if english:
            self.text("ATICADORES LTDA", (W//2, 116), 50, GOLD, True)
            self.text("THE GAME", (W//2, 172), 25, WHITE, True)
        mouse = pygame.mouse.get_pos()
        sw, sh = self.screen.get_size()
        mouse = (mouse[0]*W/max(1, sw), mouse[1]*H/max(1, sh))
        cursor_hand = False
        keys = ("play", "options", "credits", "quit")
        labels = ("PLAY", "OPTIONS", "CREDITS", "QUIT") if english else ("JOGAR", "OPÇÕES", "CRÉDITOS", "SAIR")
        positions = ((81, 245, 330, 98), (80, 338, 330, 92), (82, 425, 330, 90), (84, 513, 330, 81))
        for key, label, values, sprites in zip(keys, labels, positions, self.menu_buttons):
            rect = pygame.Rect(values)
            hovered = rect.collidepoint(mouse)
            pressed = hovered and pygame.mouse.get_pressed()[0]
            cursor_hand |= hovered
            self.controls.append((key, rect))
            if not english:
                sprite = sprites[1] if pressed else sprites[2] if hovered else sprites[0]
                if sprite:
                    self.canvas.blit(pygame.transform.scale(sprite, rect.size), rect)
                else:
                    self.button(key, label, rect, font=22)
            else:
                color = (48, 94, 132) if hovered else (28, 55, 88)
                pygame.draw.rect(self.canvas, color, rect, border_radius=8)
                pygame.draw.rect(self.canvas, GOLD if hovered else CYAN, rect, 2, border_radius=8)
                self.text(label, rect.center, 22, WHITE, True)
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND if cursor_hand else pygame.SYSTEM_CURSOR_ARROW)
        if not english:
            self.text("Versão Beta", (32, 685), 14, (170, 170, 180))
        if self.credits:
            self.panel(pygame.Rect(355, 190, 570, 340), (12, 18, 42, 250), GOLD)
            self.text(self.tx("CRÉDITOS", "CREDITS"), (640, 233), 32, GOLD, True)
            details = ("ATICADORES LTDA - O Jogo\nDesenvolvido por: Aticadores LTDA\nEscola Técnica Estadual\nAdvogado José David Gil Rodrigues\n\nMotor: Pygame\nAno: 2025\n\nObrigado por jogar!" if self.settings["language"] == "pt_BR" else
                       "ATICADORES LTDA - The Game\nDeveloped by: Aticadores LTDA\nState Technical School\nAdvogado Jose David Gil Rodrigues\n\nEngine: Pygame\nYear: 2025\n\nThanks for playing!")
            self.wrapped(details, pygame.Rect(420, 280, 440, 205), 21)
            self.button("close_credits", self.tx("FECHAR", "CLOSE"), pygame.Rect(540, 470, 200, 45))
        if self.saved_prompt:
            self.panel(pygame.Rect(350, 220, 580, 285), (12, 18, 42, 250), GOLD)
            self.text(self.tx("Partida salva encontrada", "Saved game found"), (640, 263), 29, GOLD, True)
            self.button("resume_saved", self.tx("CONTINUAR", "CONTINUE"), pygame.Rect(395, 365, 150, 52), font=18)
            self.button("new_saved", self.tx("NOVO JOGO", "NEW GAME"), pygame.Rect(565, 365, 150, 52), font=18)
            self.button("cancel_saved", self.tx("CANCELAR", "CANCEL"), pygame.Rect(735, 365, 150, 52), font=18)

    def render_character(self):
        self.bg_image("select_bg", 145)
        self.button("back", "← VOLTAR", pygame.Rect(18, 18, 145, 46), font=18)
        self.panel(pygame.Rect(250, 80, 780, 570), (14, 20, 47, 235))
        self.text(self.tx("ESCOLHA SEU PERSONAGEM", "CHOOSE YOUR CHARACTER"), (640, 125), 30, GOLD, True)
        self.text(self.tx("Qual o nome do jogador?", "Player name?"), (410, 200), 20, WHITE)
        field = pygame.Rect(660, 190, 260, 44)
        pygame.draw.rect(self.canvas, (245, 245, 250), field, border_radius=5)
        pygame.draw.rect(self.canvas, CYAN, field, 2, border_radius=5)
        shown_name = self.name_edit or (self.name if self.name != "Jogador" else "")
        self.text(shown_name or self.tx("Digite aqui...", "Type here..."), (field.x+12, field.y+10), 18, (45, 45, 55) if shown_name else (135, 135, 145))
        self.controls.append(("name_field", field))
        if self.feedback:
            self.text(self.feedback, (640, 250), 17, (255, 110, 110), True)
        self.button("prev_char", "<", pygame.Rect(390, 325, 60, 58), font=28)
        self.button("next_char", ">", pygame.Rect(830, 325, 60, 58), font=28)
        gender = "boy" if self.char_index == 0 else "girl"
        self.image_fit(gender, pygame.Rect(570, 260, 140, 180))
        self.text(self.tx("Masculino", "Male") if self.char_index == 0 else self.tx("Feminino", "Female"), (640, 455), 22, CYAN, True)
        self.text(self.tx("ESCOLHA A DIFICULDADE", "CHOOSE DIFFICULTY"), (640, 488), 17, GOLD, True)
        mouse = pygame.mouse.get_pos()
        sw, sh = self.screen.get_size()
        mouse = (mouse[0]*W/max(1, sw), mouse[1]*H/max(1, sh))
        for i, level in enumerate(self.DIFFICULTY_ORDER):
            rect = pygame.Rect(292+i*174, 510, 164, 45)
            selected = level == self.difficulty
            hovered = rect.collidepoint(mouse)
            color = (38, 105, 78) if selected else (48, 94, 132) if hovered else (28, 55, 88)
            pygame.draw.rect(self.canvas, color, rect, border_radius=8)
            pygame.draw.rect(self.canvas, GOLD if selected else CYAN, rect, 2, border_radius=8)
            self.text(self.difficulty_name(level), rect.center, 15, WHITE, True)
            self.controls.append(("difficulty_"+level, rect))
        if self.difficulty in ("hard", "impossible"):
            self.text(self.tx("No Difícil e Impossível: segure C ou Shift; cada bloqueio segura 1 ataque", "On Hard and Impossible: hold C or Shift; each block stops 1 attack"), (640, 563), 13, (180, 220, 240), True)
        self.button("confirm", self.tx("COMEÇAR", "START"), pygame.Rect(560, 590, 160, 48), font=22)

    def render_settings(self):
        values = self.settings_draft
        self.canvas.fill((10, 15, 49))
        self.panel(pygame.Rect(210, 38, 860, 644), (22, 29, 62, 255))
        self.text(self.tx("CONFIGURAÇÕES", "SETTINGS"), (640, 78), 30, GOLD, True)
        self.text(self.tx("TELA", "DISPLAY"), (300, 130), 20, CYAN)
        self.button("fullscreen", "☑ "+self.tx("Tela cheia", "Fullscreen") if values["fullscreen"] else "□ "+self.tx("Tela cheia", "Fullscreen"), pygame.Rect(300, 163, 260, 42), font=18)
        self.draw_slider("brightness", self.tx("Brilho", "Brightness"), 240)
        self.text(self.tx("ÁUDIO", "AUDIO"), (300, 300), 20, CYAN)
        self.draw_slider("master", self.tx("Volume geral", "Master volume"), 338)
        self.draw_slider("sfx", self.tx("Efeitos sonoros", "Sound effects"), 395)
        self.text(self.tx("MÚSICA", "MUSIC"), (300, 463), 20, CYAN)
        self.draw_slider("music", self.tx("Volume da música", "Music volume"), 501)
        self.text(self.tx("IDIOMA", "LANGUAGE"), (740, 130), 20, CYAN)
        self.button("language", "Português (Brasil)" if values["language"] == "pt_BR" else "English", pygame.Rect(740, 163, 270, 42), font=17)
        self.text(self.tx("DADOS SALVOS", "SAVED DATA"), (740, 245), 20, CYAN)
        self.button("clear_save", self.tx("EXCLUIR DADOS SALVOS", "CLEAR SAVED SETTINGS"), pygame.Rect(740, 280, 270, 45), font=16)
        if self.feedback:
            self.text(self.feedback, (740, 350), 16, (100, 240, 150))
        cancel_label = self.tx("VOLTAR À PAUSA", "BACK TO PAUSE") if self.settings_return_to_pause else self.tx("CANCELAR", "CANCEL")
        self.button("cancel_settings", cancel_label, pygame.Rect(710, 600, 155, 46), font=17)
        self.button("save_settings", self.tx("SALVAR", "SAVE"), pygame.Rect(880, 600, 130, 46), font=17)

    def render_pause(self):
        shade = pygame.Surface((W, H), pygame.SRCALPHA)
        shade.fill((0, 0, 0, 175))
        self.canvas.blit(shade, (0, 0))
        self.panel(pygame.Rect(390, 170, 500, 390), (15, 22, 48, 250), GOLD)
        self.text(self.tx("PAUSADO", "PAUSED"), (640, 225), 36, GOLD, True)
        self.button("pause_resume", self.tx("RETORNAR AO JOGO", "RESUME GAME"), pygame.Rect(505, 290, 270, 55), font=20)
        self.button("pause_settings", self.tx("CONFIGURAÇÕES", "SETTINGS"), pygame.Rect(505, 370, 270, 55), font=20)
        self.button("pause_save_exit", self.tx("SALVAR E SAIR", "SAVE AND EXIT"), pygame.Rect(505, 450, 270, 55), font=20)
        if self.feedback:
            self.text(self.feedback, (640, 525), 16, (255, 130, 130), True)

    def draw_slider(self, key, label, y):
        self.text(label, (300, y), 17)
        track = pygame.Rect(465, y+7, 250, 12)
        pygame.draw.rect(self.canvas, (60, 68, 90), track, border_radius=6)
        val = float(self.settings_draft[key])
        pygame.draw.rect(self.canvas, CYAN, (track.x, track.y, int(track.w*val), track.h), border_radius=6)
        pygame.draw.circle(self.canvas, WHITE, (track.x+int(track.w*val), track.centery), 10)
        self.text(f"{round(val*100)}", (730, y-1), 17)
        self.controls.append(("slider_"+key, track.inflate(0, 24)))

    def draw_classroom_desk(self, x, y):
        # Carteira escolar em vista superior estilizada, com cadeira, pés e caderno.
        pygame.draw.ellipse(self.canvas, (68, 47, 34), (x-2, y+38, 112, 30))
        pygame.draw.rect(self.canvas, (81, 57, 39), (x+31, y+42, 48, 25))
        pygame.draw.rect(self.canvas, (37, 34, 34), (x+35, y+45, 6, 20))
        pygame.draw.rect(self.canvas, (37, 34, 34), (x+69, y+45, 6, 20))
        pygame.draw.rect(self.canvas, (50, 35, 26), (x, y, 108, 50))
        pygame.draw.rect(self.canvas, (152, 103, 57), (x+3, y+3, 102, 43))
        pygame.draw.rect(self.canvas, (181, 131, 78), (x+6, y+6, 96, 34))
        pygame.draw.line(self.canvas, (205, 159, 101), (x+8, y+8), (x+98, y+8), 2)
        pygame.draw.rect(self.canvas, (226, 220, 195), (x+36, y+12, 30, 20))
        pygame.draw.rect(self.canvas, (105, 91, 72), (x+36, y+12, 30, 20), 2)
        pygame.draw.line(self.canvas, (164, 151, 129), (x+41, y+18), (x+59, y+18), 1)
        pygame.draw.line(self.canvas, (164, 151, 129), (x+41, y+23), (x+57, y+23), 1)

    def draw_battle_room(self):
        self.canvas.fill((125, 91, 58))
        # Madeira em tábuas com veios e emendas alternadas.
        plank_h = 34
        for row, y in enumerate(range(96, H-38, plank_h)):
            shade = (145, 101, 62) if row % 2 == 0 else (133, 91, 56)
            pygame.draw.rect(self.canvas, shade, (36, y, W-72, plank_h))
            pygame.draw.line(self.canvas, (91, 62, 43), (36, y), (W-36, y), 2)
            seam_offset = 115 if row % 2 else 0
            for seam_x in range(36+seam_offset, W-36, 230):
                pygame.draw.line(self.canvas, (100, 68, 46), (seam_x, y+2), (seam_x, min(y+plank_h-2, H-38)), 2)
            for grain in range(5):
                gx = 55 + ((row*173 + grain*239) % (W-110))
                gy = y + 7 + (grain*11 % 20)
                pygame.draw.line(self.canvas, (159, 115, 71), (gx, gy), (min(gx+18+(grain%4)*6, W-40), gy), 1)
        # Paredes pintadas, painéis e rodapé de madeira.
        pygame.draw.rect(self.canvas, (57, 76, 69), (0, 0, W, 96))
        pygame.draw.rect(self.canvas, (68, 91, 79), (0, 0, W, 77))
        door_y, door_h = 322, 150
        pygame.draw.rect(self.canvas, (48, 62, 58), (0, 0, 36, H))
        pygame.draw.rect(self.canvas, (48, 62, 58), (W-36, 0, 36, H))
        pygame.draw.rect(self.canvas, (54, 43, 35), (0, H-38, W, 38))
        for x in range(48, W-40, 112):
            pygame.draw.rect(self.canvas, (78, 103, 89), (x, 17, 88, 57))
            pygame.draw.line(self.canvas, (91, 118, 99), (x+7, 25), (x+79, 25), 2)
            pygame.draw.line(self.canvas, (53, 73, 66), (x+4, 70), (x+84, 70), 2)
        pygame.draw.rect(self.canvas, (35, 29, 27), (0, 88, W, 11))
        pygame.draw.rect(self.canvas, (115, 75, 45), (0, 92, W, 7))
        pygame.draw.rect(self.canvas, (106, 69, 43), (0, H-48, W, 10))

        # Porta fechada vista de cima, encaixada no vão da parede esquerda.
        pygame.draw.rect(self.canvas, (31, 25, 23), (0, door_y-4, 47, door_h+8))
        pygame.draw.rect(self.canvas, (113, 68, 42), (2, door_y, 42, door_h))
        pygame.draw.rect(self.canvas, (151, 91, 52), (6, door_y+4, 34, door_h-8))
        pygame.draw.line(self.canvas, (181, 116, 69), (10, door_y+8), (10, door_y+door_h-8), 2)
        pygame.draw.line(self.canvas, (91, 53, 36), (36, door_y+8), (36, door_y+door_h-8), 2)
        pygame.draw.rect(self.canvas, (89, 53, 36), (11, door_y+16, 23, 48), 2)
        pygame.draw.rect(self.canvas, (89, 53, 36), (11, door_y+86, 23, 48), 2)
        pygame.draw.rect(self.canvas, (207, 173, 101), (39, door_y+door_h//2-3, 4, 7))
        pygame.draw.rect(self.canvas, (67, 44, 33), (2, door_y+25, 4, 8))
        pygame.draw.rect(self.canvas, (67, 44, 33), (2, door_y+door_h-33, 4, 8))

        # Carteiras nas laterais e no fundo, preservando o espaço central da luta.
        for x, y in self.CLASSROOM_DESKS:
            self.draw_classroom_desk(x, y)

    def move_with_room_collision(self, position, movement, radius=12):
        """Move an actor around chairs and the professor while allowing it to slide."""
        obstacles = [pygame.Rect(x+31, y+42, 48, 25) for x, y in self.CLASSROOM_DESKS]
        obstacles.append(pygame.Rect(278, 321, 56, 37))
        for axis in ("x", "y"):
            candidate = position.copy()
            setattr(candidate, axis, getattr(candidate, axis)+getattr(movement, axis))
            candidate.x = max(48, min(W-48, candidate.x))
            candidate.y = max(76, min(H-58, candidate.y))
            feet_box = pygame.Rect(round(candidate.x-radius), round(candidate.y-radius),
                                   radius*2, radius*2)
            if not any(feet_box.colliderect(obstacle) for obstacle in obstacles):
                setattr(position, axis, getattr(candidate, axis))

    def render_game(self):
        self.draw_battle_room()
        pygame.draw.rect(self.canvas, (26, 77, 39), (340, 8, 600, 56))
        self.text(self.tx("Sala da Batalha", "Battle Room"), (640, 35), 18, (220, 255, 220), True)
        self.draw_projectiles()
        self.draw_person(self.boss, "boss")
        self.draw_person(self.player, "player")
        # professor guide
        self.image_fit("professor", pygame.Rect(275, 275, 62, 82))
        self.text("Professor", (306, 260), 14, GOLD, True)
        self.text(f"{self.tx('Chefão', 'Boss')}  {self.boss_hp} / {self.boss_hp_max}", (640, 77), 15, (255, 130, 130), True)
        self.draw_bar(pygame.Rect(390, 88, 500, 22), self.boss_hp, self.boss_hp_max, (205, 55, 55))
        self.text(f"{self.tx('Dificuldade', 'Difficulty')}: {self.difficulty_name()}", (120, 78), 14, GOLD, True)
        self.text(self.name, (640, 634), 14, CYAN, True)
        self.draw_player_hearts()
        if self.phase == "intro":
            self.draw_dialogue()
        if self.phase == "lost":
            self.render_death_popup()

    def render_death_popup(self):
        progress = min(1.0, max(0.0, self.state_time/.45))
        shade = pygame.Surface((W, H), pygame.SRCALPHA)
        shade.fill((0, 0, 0, int(180*progress)))
        self.canvas.blit(shade, (0, 0))
        scale = .86 + .14*progress
        panel_w, panel_h = int(500*scale), int(315*scale)
        panel_rect = pygame.Rect(0, 0, panel_w, panel_h)
        panel_rect.center = (W//2, int(350 + 24*(1-progress)))
        self.panel(panel_rect, (34, 18, 28, int(250*progress)), (255, 105, 105), 16)
        self.text(self.tx("VOCÊ MORREU!", "YOU DIED!"), (640, panel_rect.y+72), 40, (255, 105, 105), True)
        self.text(self.tx("A batalha foi perdida.", "The battle is over."), (640, panel_rect.y+125), 20, (225, 220, 220), True)
        if progress >= .65:
            button_y = panel_rect.y + 177
            self.button("retry_death", self.tx("TENTAR NOVAMENTE", "TRY AGAIN"), pygame.Rect(475, button_y, 330, 48), font=18)
            self.button("menu_death", self.tx("VOLTAR AO MENU PRINCIPAL", "BACK TO MAIN MENU"), pygame.Rect(475, button_y+62, 330, 48), font=17)

    def draw_person(self, pos, kind):
        x, y = round(pos.x), round(pos.y)
        if kind == "boss":
            index = int(self.boss_action_time*7) % 2 if self.boss_action in ("attack", "hurt") else int(self.boss_anim_time*3.5) % 2 if self.boss_moving else 0
            if self.boss_action == "attack": source = self.boss_attack_sprites[index]
            elif self.boss_action == "hurt": source = self.boss_hurt_sprites[index]
            else: source = self.boss_sprites[index]
            sprite = pygame.transform.scale(source, (84, 112))
            if self.boss_direction.x < -.25:
                sprite = pygame.transform.flip(sprite, True, False)
            if self.boss_action == "hurt" or self.attack_flash > 0:
                sprite.fill((95, 25, 25, 0), special_flags=pygame.BLEND_RGBA_ADD)
            self.canvas.blit(sprite, (x-42, y-96))
            self.text("!! "+self.tx("CHEFÃO", "BOSS")+" !!", (x, y-103), 15, (255, 90, 90), True)
            if self.impact_timer > 0 and pos.distance_to(self.impact_position) < 1:
                self.draw_impact(x, y-45)
        else:
            if self.phase == "lost":
                facing = "up" if self.direction.y < -.45 else "down" if self.direction.y > .45 else "side"
                fallen = pygame.transform.scale(self.player_hurt_frames[self.gender][facing], (60, 96))
                fallen.fill((120, 25, 30, 0), special_flags=pygame.BLEND_RGBA_ADD)
                angle = min(90, self.state_time*180)
                fallen = pygame.transform.rotate(fallen, angle)
                self.canvas.blit(fallen, fallen.get_rect(center=(x, y-40)))
                return
            animations = self.player_frames.get(self.gender, {})
            facing_direction = self.player_action_direction if self.player_action == "punch" else self.direction
            if facing_direction.y < -.45:
                facing, key = "up", "walk_up" if self.player_moving else "idle_up"
            elif facing_direction.y > .45:
                facing, key = "down", "walk_down" if self.player_moving else "idle_down"
            elif facing_direction.x < 0:
                facing, key = "side", "walk_left" if self.player_moving else "idle_side"
            else:
                facing, key = "side", "walk_right" if self.player_moving else "idle_side"
            frames = animations.get(key, [])
            if not frames and not self.player_moving:
                frames = animations.get("idle_down", [])
            if self.player_blocking:
                frame = self.player_block_frames[self.gender][facing]
            elif self.player_action == "punch":
                punch_frames = self.player_punch_frames[self.gender][facing]
                frame = punch_frames[min(1, int(self.player_action_time*8))]
            elif self.player_action == "hurt":
                frame = self.player_hurt_frames[self.gender][facing]
            elif frames:
                frame_index = int(self.walk_anim_time*4) % len(frames) if self.player_moving else 0
                frame = frames[frame_index]
            else:
                frame = None
            if frame:
                sprite = pygame.transform.scale(frame, (60, 96))
                if self.player_action == "punch" and facing == "side" and self.player_action_direction.x < 0:
                    sprite = pygame.transform.flip(sprite, True, False)
                if self.player_blocking and facing == "side" and self.direction.x < 0:
                    sprite = pygame.transform.flip(sprite, True, False)
                if self.player_action == "hurt":
                    sprite.fill((100, 20, 25, 0), special_flags=pygame.BLEND_RGBA_ADD)
                self.canvas.blit(sprite, (x-30, y-88))
                if self.player_blocking or self.block_flash > 0:
                    pygame.draw.ellipse(self.canvas, (95, 205, 255), (x-39, y-89, 78, 98), 3)
            else:
                pygame.draw.rect(self.canvas, (55, 105, 205), (x-14, y-22, 28, 36), border_radius=4)
                pygame.draw.rect(self.canvas, (240, 205, 160), (x-11, y-38, 22, 16), border_radius=6)
            self.text(self.name, (x, y-98), 14, CYAN, True)
            if self.impact_timer > 0 and pos.distance_to(self.impact_position) < 1:
                self.draw_impact(x, y-43)

    def draw_projectiles(self):
        for shot in self.projectiles:
            x, y = round(shot["pos"].x), round(shot["pos"].y)
            kind = shot["kind"]
            if kind == "rock":
                pygame.draw.polygon(self.canvas, (117, 119, 126), [(x-13,y-4),(x-8,y-13),(x+5,y-14),(x+14,y-3),(x+10,y+10),(x-6,y+12),(x-14,y+4)])
                pygame.draw.polygon(self.canvas, (170, 173, 179), [(x-8,y-6),(x-4,y-10),(x+4,y-10),(x+7,y-4)])
            elif kind == "paper":
                pygame.draw.rect(self.canvas, (245, 239, 214), (x-12,y-14,24,28), border_radius=2)
                pygame.draw.rect(self.canvas, (190, 180, 151), (x-12,y-14,24,28), 2, border_radius=2)
                pygame.draw.line(self.canvas, (195,187,164), (x-7,y-5), (x+7,y-5), 2)
                pygame.draw.line(self.canvas, (195,187,164), (x-7,y+1), (x+7,y+1), 2)
            else:
                pygame.draw.line(self.canvas, (205, 218, 228), (x-11,y+10), (x+10,y-11), 5)
                pygame.draw.line(self.canvas, (218, 90, 92), (x-10,y-11), (x+11,y+10), 5)
                pygame.draw.circle(self.canvas, GOLD, (x,y), 4)
        for shot in self.paper_projectiles:
            x, y = round(shot["pos"].x), round(shot["pos"].y)
            pygame.draw.rect(self.canvas, (193, 181, 151), (x-9, y-6, 18, 12))
            pygame.draw.rect(self.canvas, (250, 246, 222), (x-6, y-9, 12, 18))
            pygame.draw.rect(self.canvas, (255, 255, 239), (x-3, y-6, 6, 12))
            pygame.draw.rect(self.canvas, (212, 203, 179), (x, y-3, 6, 6))

    def throw_paper(self, aim_point):
        if self.state != "game" or self.paused or self.phase != "combat" or self.boss_hp <= 0 or self.paper_cooldown > 0:
            return
        origin = self.player + pygame.Vector2(0, -48)
        target = pygame.Vector2(aim_point)
        direction = target-origin
        if not direction.length_squared(): direction = self.direction.copy()
        if not direction.length_squared(): direction = pygame.Vector2(0, -1)
        direction = direction.normalize()
        self.paper_projectiles.append({"pos": origin, "velocity": direction*520})
        self.paper_cooldown = 5.0
        self.play_sfx("punch")

    def spawn_rps_projectile(self, profile):
        kind = random.choice(("rock", "paper", "scissors"))
        direction = self.player - self.boss
        if not direction.length_squared(): direction = pygame.Vector2(-1, 0)
        direction = direction.normalize()
        self.projectiles.append({"pos": self.boss.copy(), "velocity": direction*profile["rps_speed"],
                                 "kind": kind, "damage": profile["rps_damage"]})

    def draw_impact(self, x, y):
        color = (255, 232, 126)
        radius = 20 if self.impact_timer > .09 else 13
        pygame.draw.circle(self.canvas, color, (x, y), radius, 3)
        for angle in range(0, 360, 45):
            a = math.radians(angle)
            start = (int(x+math.cos(a)*(radius+3)), int(y+math.sin(a)*(radius+3)))
            end = (int(x+math.cos(a)*(radius+13)), int(y+math.sin(a)*(radius+13)))
            pygame.draw.line(self.canvas, color, start, end, 3)
        self.text("POW!", (x+23, y-24), 17, GOLD, True)

    def draw_bar(self, rect, value, maximum, color):
        pygame.draw.rect(self.canvas, (45, 35, 44), rect, border_radius=4)
        inside = rect.inflate(-4, -4)
        inside.w = int(inside.w * max(0, value) / maximum)
        pygame.draw.rect(self.canvas, color, inside, border_radius=3)

    def draw_player_hearts(self):
        """Desenha corações pixelados centralizados no rodapé, como no Minecraft."""
        rows = (
            (0, 1, 1, 0, 0, 1, 1, 0),
            (1, 1, 1, 1, 1, 1, 1, 1),
            (1, 1, 1, 1, 1, 1, 1, 1),
            (0, 1, 1, 1, 1, 1, 1, 0),
            (0, 0, 1, 1, 1, 1, 0, 0),
            (0, 0, 0, 1, 1, 0, 0, 0),
        )
        cell, gap = 3, 8
        heart_w = 8*cell
        total_w = self.player_hp_max*heart_w + (self.player_hp_max-1)*gap
        outline = cell
        icon_radius, icon_gap = 13, 12
        heart_outer_w = total_w + 2*outline
        combined_w = heart_outer_w + icon_gap + 2*icon_radius
        group_left = (W-combined_w)//2
        start_x = group_left + outline
        start_y = 647
        for heart_index in range(self.player_hp_max):
            filled = heart_index < self.player_hp
            heart_x = start_x+heart_index*(heart_w+gap)
            # Primeiro pinta um contorno externo contínuo, sem linhas entre os pixels vermelhos.
            for row_index, row in enumerate(rows):
                for column_index, pixel in enumerate(row):
                    if not pixel:
                        continue
                    for dr in (-1, 0, 1):
                        for dc in (-1, 0, 1):
                            neighbor_row, neighbor_column = row_index+dr, column_index+dc
                            inside = 0 <= neighbor_row < len(rows) and 0 <= neighbor_column < len(row)
                            if not inside or not rows[neighbor_row][neighbor_column]:
                                pygame.draw.rect(self.canvas, (18, 13, 19),
                                    (heart_x+neighbor_column*cell, start_y+neighbor_row*cell, cell, cell))
            for row_index, row in enumerate(rows):
                for column_index, pixel in enumerate(row):
                    if pixel:
                        color = (235, 35, 48) if filled else (105, 72, 82)
                        pygame.draw.rect(self.canvas, color,
                            (heart_x+column_index*cell, start_y+row_index*cell, cell, cell))
        icon_center = (group_left+heart_outer_w+icon_gap+icon_radius, start_y+10)
        self.draw_paper_cooldown_icon(icon_center)

    def draw_paper_cooldown_icon(self, center):
        """Anel vazado que se completa em sentido horário durante a recarga."""
        radius, width = 12, 4
        pygame.draw.circle(self.canvas, (74, 77, 83), center, radius, width)
        progress = 1.0 - max(0.0, min(5.0, self.paper_cooldown))/5.0
        segments = 64
        filled = round(segments*progress)
        previous = None
        for index in range(filled+1):
            angle = -math.pi/2 + 2*math.pi*index/segments
            point = (round(center[0]+math.cos(angle)*radius),
                     round(center[1]+math.sin(angle)*radius))
            if previous is not None:
                pygame.draw.line(self.canvas, (174, 180, 188), previous, point, width)
            previous = point

    def draw_dialogue(self):
        rect = pygame.Rect(80, 510, 1120, 195)
        self.panel(rect, (20, 22, 32, 245), (120, 140, 160))
        speaker, content = self.current_dialogue()
        self.text(speaker+":", (105, 530), 19, GOLD)
        self.wrapped(content, pygame.Rect(105, 565, 1065, 100), 18)
        self.text(self.tx("> Pressione ESPAÇO ou ENTER para continuar", "> Press SPACE or ENTER to continue"), (1175, 677), 14, (175, 175, 180), center=False)

    def current_dialogue(self):
        if self.settings["language"] == "en":
            controls = "GAME CONTROLS:\n  W / A / S / D or Arrows — Move\n  SPACE or Z — Punch"
            if self.blocking_available(): controls += "\n  Hold C or Shift — Block while held, up to one attack"
            controls += "\n  Left mouse button — Throw paper ball (40 damage)"
            seq = [
                ("Teacher (Aticadores)", f"Hey, {self.name}! Great to have you on the team!\nWe're Aticadores LTDA — the best group in school!"),
                ("Teacher (Aticadores)", "There is a hidden hierarchy here. The White Room controls everything\nand stops the fun from spreading through the school."),
                ("Teacher (Aticadores)", controls),
                ("Teacher (Aticadores)", "Look over there! The BOSS of the Battle Room is challenging us!\nHe's strong, but you can beat him with your punches. Go for it!"),
            ]
            return seq[min(self.dialogue_step, len(seq)-1)]
        controls = "CONTROLES DO JOGO:\n  W / A / S / D ou Setas — Mover\n  ESPAÇO ou Z — Dar soco"
        if self.blocking_available(): controls += "\n  Segure C ou Shift — Bloqueia enquanto pressionado, até um ataque"
        controls += "\n  Botão esquerdo do mouse — Jogar bolinha de papel (40 de dano)"
        seq = [
            ("Professor (Aticadores)", f"Ei, {self.name}! Que bom ter você na equipe!\nSomos os Aticadores LTDA — o melhor grupo da escola!"),
            ("Professor (Aticadores)", "Existe uma hierarquia oculta aqui. A Sala Branca controla tudo\ne impede que a resenha se espalhe pela escola."),
            ("Professor (Aticadores)", controls),
            ("Professor (Aticadores)", "Olha ali! O CHEFÃO da Sala da Batalha está nos desafiando!\nEle é forte, mas você consegue derrotá-lo com seus socos. Vai lá!"),
        ]
        return seq[min(self.dialogue_step, len(seq)-1)]

    def render_victory(self):
        self.canvas.fill((8, 27, 12))
        pygame.draw.rect(self.canvas, (17, 80, 36, 30), (190, 38, 900, 644))
        self.text(self.tx("*** PARABÉNS! ***", "*** CONGRATULATIONS! ***"), (640, 145), 54, GOLD, True)
        self.text(self.tx(f"{self.name} venceu!", f"{self.name} won!"), (640, 225), 31, (115, 255, 140), True)
        self.text(self.tx("Você concluiu a versão beta de", "You completed the beta version of"), (640, 330), 25, (220, 238, 250), True)
        self.text("ATICADORES LTDA - THE GAME!" if self.settings["language"] == "en" else "ATICADORES LTDA - O JOGO!", (640, 370), 25, (220, 238, 250), True)
        self.text(self.tx("O Chefão foi derrotado e a sala foi libertada!", "The boss is defeated and the room is free!"), (640, 435), 19, (185, 195, 195), True)
        self.text(self.tx("A luta dos Aticadores continua...", "The Aticadores fight continues..."), (640, 466), 19, (185, 195, 195), True)
        self.button("play_again", self.tx("JOGAR NOVAMENTE", "PLAY AGAIN"), pygame.Rect(445, 555, 195, 52), font=17)
        self.button("main_menu", self.tx("MENU PRINCIPAL", "MAIN MENU"), pygame.Rect(660, 555, 180, 52), font=17)

    def render(self):
        self.controls.clear()
        if self.state == "loading": self.render_loading()
        elif self.state == "menu": self.render_menu()
        elif self.state == "select": self.render_character()
        elif self.state == "settings": self.render_settings()
        elif self.state == "game":
            self.render_game()
            if self.paused: self.render_pause()
        elif self.state == "victory": self.render_victory()
        if self.state != "settings" and self.settings["brightness"] < 1:
            alpha = round((1-float(self.settings["brightness"])) * 170)
            shade = pygame.Surface((W, H), pygame.SRCALPHA); shade.fill((0, 0, 0, alpha)); self.canvas.blit(shade, (0, 0))
        sw, sh = self.screen.get_size()
        scaled = pygame.transform.smoothscale(self.canvas, (sw, sh))
        self.screen.blit(scaled, (0, 0))
        pygame.display.flip()

    def hit(self, key, point):
        for control, rect in self.controls:
            if control == key and rect.collidepoint(point): return True
        return False

    def handle_click(self, pos):
        sw, sh = self.screen.get_size()
        p = (pos[0]*W/max(1, sw), pos[1]*H/max(1, sh))
        if self.state == "menu":
            if self.saved_prompt:
                if self.hit("resume_saved", p):
                    if not self.load_game(): self.saved_prompt = False
                elif self.hit("new_saved", p):
                    try: self.save_path.unlink(missing_ok=True)
                    except OSError: pass
                    self.saved_prompt = False; self.name_edit = ""; self.feedback = ""; self.set_state("select")
                elif self.hit("cancel_saved", p): self.saved_prompt = False
                return
            if self.credits:
                if self.hit("close_credits", p): self.credits = False
                return
            if self.hit("play", p):
                if self.save_path.exists(): self.saved_prompt = True
                else: self.name_edit = ""; self.feedback = ""; self.set_state("select")
            elif self.hit("options", p): self.feedback = ""; self.settings_return_to_pause = False; self.settings_draft = self.settings.copy(); self.set_state("settings")
            elif self.hit("credits", p): self.credits = True
            elif self.hit("quit", p): pygame.event.post(pygame.event.Event(pygame.QUIT))
        elif self.state == "select":
            if self.hit("back", p): self.set_state("menu")
            elif self.hit("prev_char", p): self.char_index = (self.char_index-1) % 2
            elif self.hit("next_char", p): self.char_index = (self.char_index+1) % 2
            elif any(self.hit("difficulty_"+level, p) for level in self.DIFFICULTY_ORDER):
                for level in self.DIFFICULTY_ORDER:
                    if self.hit("difficulty_"+level, p): self.difficulty = level; break
            elif self.hit("confirm", p):
                candidate = self.name_edit.strip() or (self.name if self.name != "Jogador" else "")
                if not candidate: self.feedback = self.tx("Por favor, digite seu nome!", "Please enter your name!")
                else: self.name = candidate[:20]; self.gender = "boy" if self.char_index == 0 else "girl"; self.feedback = ""; self.start_game()
            elif self.hit("name_field", p): pygame.key.start_text_input()
        elif self.state == "settings":
            if self.hit("fullscreen", p): self.settings_draft["fullscreen"] = not self.settings_draft["fullscreen"]
            elif self.hit("language", p): self.settings_draft["language"] = "en" if self.settings_draft["language"] == "pt_BR" else "pt_BR"
            elif self.hit("clear_save", p):
                try: (Path.home()/".aticadores_settings.json").unlink(missing_ok=True)
                except OSError: pass
                self.settings = {"brightness": .7, "master": .8, "sfx": .8,
                                 "music": .6, "fullscreen": False, "language": "pt_BR"}
                self.settings_draft = self.settings.copy()
                self.apply_audio(self.settings)
                pygame.display.set_mode((W, H), pygame.RESIZABLE)
                self.feedback = "Configurações restauradas!" if self.settings["language"] == "pt_BR" else "Settings reset to defaults!"
                self.feedback_time = 2.0
            elif self.hit("cancel_settings", p):
                self.settings_draft = self.settings.copy()
                if self.settings_return_to_pause:
                    self.settings_return_to_pause = False; self.set_state("game"); self.paused = True
                else: self.set_state("menu")
            elif self.hit("save_settings", p):
                self.settings = self.settings_draft.copy()
                self.save_settings()
                self.apply_audio(self.settings)
                if self.settings["fullscreen"]: pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                else: pygame.display.set_mode((W, H), pygame.RESIZABLE)
                self.feedback = self.tx("Configurações salvas!", "Settings saved!")
                if self.settings_return_to_pause:
                    self.settings_return_to_pause = False; self.set_state("game"); self.paused = True
                else: self.set_state("menu")
            else:
                for k in ("brightness", "master", "sfx", "music"):
                    if self.hit("slider_"+k, p): self.set_slider(k, p[0])
        elif self.state == "game":
            if self.phase == "lost":
                if self.hit("retry_death", p): self.start_game()
                elif self.hit("menu_death", p): self.paused = False; self.set_music(); self.set_state("menu")
            elif self.paused:
                if self.hit("pause_resume", p): self.paused = False
                elif self.hit("pause_settings", p):
                    self.settings_return_to_pause = True
                    self.settings_draft = self.settings.copy()
                    self.set_state("settings")
                elif self.hit("pause_save_exit", p):
                    if self.save_game(): self.paused = False; self.saved_prompt = False; self.set_state("menu")
                    else: self.feedback = self.tx("Não foi possível salvar a partida.", "Could not save the game.")
            elif self.phase == "intro": self.advance_dialogue()
        elif self.state == "victory":
            if self.hit("play_again", p): self.name_edit = self.name; self.set_state("select")
            elif self.hit("main_menu", p): self.set_state("menu")

    def set_slider(self, key, x):
        track_left, track_width = 465, 250
        self.settings_draft[key] = min(1, max(0, (x-track_left)/track_width))

    def advance_dialogue(self):
        self.dialogue_step += 1
        if self.dialogue_step >= 4:
            self.phase = "combat"
            self.set_music(fast=True)

    def update_game(self, dt):
        if self.phase == "lost":
            return
        if self.phase == "won":
            if self.state_time > 1.5: self.set_state("victory")
            return
        if self.phase != "combat": return
        self.paper_cooldown = max(0.0, self.paper_cooldown-dt)
        keys = pygame.key.get_pressed()
        self.block_flash = max(0.0, self.block_flash-dt)
        move = pygame.Vector2(int(keys[pygame.K_d] or keys[pygame.K_RIGHT])-int(keys[pygame.K_a] or keys[pygame.K_LEFT]),
                              int(keys[pygame.K_s] or keys[pygame.K_DOWN])-int(keys[pygame.K_w] or keys[pygame.K_UP]))
        if move.length_squared():
            self.direction = move.normalize()
            previous_player = self.player.copy()
            travel = self.direction * (115 if self.player_blocking else 200) * dt
            self.move_with_room_collision(self.player, travel, radius=12)
            self.player_moving = self.player.distance_to(previous_player) > .05
        else:
            self.player_moving = False
        if self.player_moving:
            self.walk_anim_time += dt
        else:
            self.walk_anim_time = 0.0

        self.attack_timer = max(0.0, self.attack_timer-dt)
        self.player_hurt_timer = max(0.0, self.player_hurt_timer-dt)
        self.boss_hurt_timer = max(0.0, self.boss_hurt_timer-dt)
        self.attack_flash = max(0.0, self.attack_flash-dt)
        self.impact_timer = max(0.0, self.impact_timer-dt)
        profile = self.difficulty_profile()
        if self.player_action == "punch":
            self.player_action_time += dt
            if self.player_action_time >= .13 and not self.player_action_hit:
                self.player_action_hit = True
                target = self.player + self.player_action_direction*44
                if self.boss.distance_to(target) <= 62:
                    self.damage_boss(20)
            if self.player_action_time >= .38:
                self.player_action = "idle"
        elif self.player_action == "hurt":
            self.player_action_time += dt
            if self.player_action_time >= .34: self.player_action = "idle"

        diff = self.player - self.boss
        if diff.length_squared(): self.boss_direction = diff.normalize()
        old_boss = self.boss.copy()
        if diff.length_squared():
            travel = diff.normalize() * min(profile["speed"]*dt, diff.length())
            self.move_with_room_collision(self.boss, travel, radius=20)
        self.boss_moving = self.boss.distance_to(old_boss) > .05
        if self.boss_moving:
            self.boss_anim_time += dt
        else:
            self.boss_anim_time = 0.0
        if self.boss_action == "attack":
            self.boss_action_time += dt
            if self.boss_action_time >= .25 and not self.boss_action_hit:
                self.boss_action_hit = True
                if self.player.distance_to(self.boss) <= 88: self.damage_player(profile["damage"])
            if self.boss_action_time >= .58: self.boss_action = "idle"
        elif self.boss_action == "hurt":
            self.boss_action_time += dt
            if self.boss_action_time >= .30: self.boss_action = "idle"
        if self.boss_action == "idle":
            self.boss_attack_timer += dt
            if self.boss_attack_timer >= profile["interval"]:
                self.boss_attack_timer = 0.0
                if self.player.distance_to(self.boss) <= 88:
                    self.boss_action = "attack"
                    self.boss_action_time = 0.0
                    self.boss_action_hit = False
        if profile["rps_interval"]:
            self.rps_attack_timer += dt
            if self.rps_attack_timer >= profile["rps_interval"] and len(self.projectiles) < 3:
                self.rps_attack_timer = 0.0
                self.spawn_rps_projectile(profile)
        for shot in self.projectiles[:]:
            shot["pos"] += shot["velocity"]*dt
            if shot["pos"].distance_to(self.player) < 30:
                self.damage_player(shot["damage"])
                self.projectiles.remove(shot)
            elif not pygame.Rect(-40, -40, W+80, H+80).collidepoint(shot["pos"].x, shot["pos"].y):
                self.projectiles.remove(shot)
        for shot in self.paper_projectiles[:]:
            shot["pos"] += shot["velocity"]*dt
            if shot["pos"].distance_to(self.boss + pygame.Vector2(0, -52)) < 42:
                self.paper_projectiles.remove(shot)
                self.damage_boss(40)
                if self.phase != "combat":
                    self.paper_projectiles.clear()
                    break
            elif not pygame.Rect(-40, -40, W+80, H+80).collidepoint(shot["pos"].x, shot["pos"].y):
                self.paper_projectiles.remove(shot)

    def damage_player(self, amount):
        if self.player_hp <= 0: return
        if self.player_blocking:
            self.player_blocking = False
            self.block_press_consumed = True
            self.block_flash = .22
            self.play_sfx("block")
            self.impact_position = self.player.copy()
            self.impact_timer = .14
            return
        self.player_hp = max(0, self.player_hp-1)
        self.player_action = "hurt"
        self.player_action_time = 0.0
        self.player_hurt_timer = .34
        self.player_action_hit = False
        self.play_sfx("hit")
        self.impact_position = self.player.copy()
        self.impact_timer = .18
        if self.player_hp <= 0:
            self.phase = "lost"
            self.state_time = 0
            self.player_action = "dead"
            self.player_action_time = 0.0
            self.paused = False
            self.boss_action = "idle"
            self.set_music(sad=True)

    def damage_boss(self, amount):
        if self.boss_hp <= 0: return
        self.boss_hp = max(0, self.boss_hp-amount)
        self.boss_action = "hurt"
        self.boss_action_time = 0.0
        self.boss_hurt_timer = .30
        self.boss_action_hit = False
        self.attack_flash = .18
        self.play_sfx("hit")
        self.impact_position = self.boss.copy()
        self.impact_timer = .18
        if self.boss_hp <= 0:
            self.phase = "won"
            self.state_time = 0
            self.boss_action = "hurt"
            self.set_music()
            self.play_sfx("victory")
            try: self.save_path.unlink(missing_ok=True)
            except OSError: pass

    def punch(self):
        if self.phase != "combat" or self.attack_timer > 0 or self.player_action == "hurt" or self.player_blocking: return
        self.attack_timer = .5
        self.play_sfx("punch")
        self.player_action = "punch"
        self.player_action_time = 0.0
        self.player_action_hit = False
        self.player_action_direction = self.direction.copy()

    def arm_block(self):
        """Arma um bloqueio enquanto C/Shift estiver pressionado, uma vez por acionamento."""
        if self.phase == "combat" and self.blocking_available() and self.player_action != "hurt" and not self.block_press_consumed:
            self.player_blocking = True

    def run(self):
        running = True
        while running:
            dt = min(self.clock.tick(FPS)/1000, .05)
            if not (self.state == "game" and self.paused): self.state_time += dt
            self.feedback_time = max(0, self.feedback_time-dt)
            if self.feedback_time == 0 and self.state == "settings": self.feedback = ""
            for event in pygame.event.get():
                if event.type == pygame.QUIT: running = False
                elif event.type == pygame.VIDEORESIZE and not self.settings["fullscreen"]:
                    self.screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    pos = (event.pos[0]*W/max(1,self.screen.get_width()), event.pos[1]*H/max(1,self.screen.get_height()))
                    if self.state == "game" and not self.paused and self.phase == "combat":
                        self.throw_paper(pos)
                    else:
                        self.play_sfx("click")
                    if self.state == "settings":
                        for k in ("brightness", "master", "sfx", "music"):
                            if self.hit("slider_"+k, pos): self.slider_drag = k; self.set_slider(k, pos[0])
                    self.handle_click(event.pos)
                elif event.type == pygame.MOUSEBUTTONUP: self.slider_drag = None
                elif event.type == pygame.MOUSEMOTION and self.slider_drag:
                    pos = (event.pos[0]*W/max(1,self.screen.get_width()), event.pos[1]*H/max(1,self.screen.get_height()))
                    self.set_slider(self.slider_drag, pos[0])
                elif event.type == pygame.KEYUP and event.key in (pygame.K_c, pygame.K_LSHIFT, pygame.K_RSHIFT):
                    self.block_keys_down.discard(event.key)
                    if not self.block_keys_down:
                        self.player_blocking = False
                        self.block_press_consumed = False
                elif event.type == pygame.KEYDOWN:
                    block_key = event.key in (pygame.K_c, pygame.K_LSHIFT, pygame.K_RSHIFT)
                    if block_key and not getattr(event, "repeat", False):
                        self.block_keys_down.add(event.key)
                    if event.key == pygame.K_ESCAPE:
                        if self.state == "game" and self.phase == "lost": self.set_music(); self.set_state("menu")
                        elif self.state == "game": self.paused = not self.paused
                        elif self.state == "settings" and self.settings_return_to_pause:
                            self.settings_draft = self.settings.copy()
                            self.settings_return_to_pause = False
                            self.set_state("game")
                            self.paused = True
                        elif self.state in ("select", "settings"): self.set_state("menu")
                        elif self.saved_prompt: self.saved_prompt = False
                        elif self.credits: self.credits = False
                    elif self.state == "select" and event.key == pygame.K_BACKSPACE:
                        if self.name_edit: self.name_edit = self.name_edit[:-1]
                    elif self.state == "select" and event.unicode and event.unicode.isprintable() and len(self.name_edit) < 20:
                        self.name_edit += event.unicode
                    elif self.state == "game":
                        if not self.paused:
                            if self.phase == "intro" and event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_KP_ENTER): self.advance_dialogue()
                            elif self.phase == "combat" and block_key and not getattr(event, "repeat", False) and self.blocking_available() and self.player_action != "hurt":
                                self.arm_block()
                            elif event.key in (pygame.K_SPACE, pygame.K_z): self.punch()
            if self.state == "game" and not self.paused: self.update_game(dt)
            if self.state == "loading" and self.progress >= 100:
                self.load_tick += dt
                if self.load_tick >= .6: self.set_state("menu")
            self.render()
        pygame.quit()
        return 0


if __name__ == "__main__":
    sys.exit(Game().run())
