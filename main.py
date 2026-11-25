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

from campaign import CHAPTERS, ROLES, ROOMS, VERDICTS
from chip_audio import RATE, speech_pcm, theme_pcm
from pixel_people import projectile, sprite
from school_maps import CLASSROOM_DESKS, FURNITURE, build_maps, campus

W, H = 1280, 720
FPS = 60
WHITE = (247, 240, 220)
GOLD = (249, 201, 116)
CYAN = (139, 221, 201)
LOGO_COLORS = ((255, 198, 57), (68, 209, 255), (140, 223, 57), (255, 92, 87), (194, 112, 253))


class Game:
    DOORWAY = pygame.Rect(1214, 526, 45, 88)
    ARENA = pygame.Rect(555, 275, 170, 148)
    BOSS_STYLES = ("Rafa", "Bia", "Prof. André", "Alex")
    DIFFICULTIES = {
        "easy": {"hp": 200, "speed": 65, "interval": 1.8, "damage": 10, "rps_interval": None, "rps_speed": 0, "rps_damage": 0},
        "medium": {"hp": 230, "speed": 78, "interval": 1.55, "damage": 12, "rps_interval": None, "rps_speed": 0, "rps_damage": 0},
        "hard": {"hp": 260, "speed": 92, "interval": 1.25, "damage": 14, "rps_interval": 4.2, "rps_speed": 245, "rps_damage": 14},
        "impossible": {"hp": 400, "speed": 180, "interval": .72, "damage": 20, "rps_interval": 2.5, "rps_speed": 340, "rps_damage": 18},
    }
    DIFFICULTY_ORDER = ("easy", "medium", "hard", "impossible")

    def __init__(self):
        pygame.mixer.pre_init(RATE, -16, 2, 512)
        pygame.init()
        pygame.display.set_caption("Atiçadores LTDA — O Jogo")
        self.screen = pygame.display.set_mode((W, H), pygame.RESIZABLE)
        self.canvas = pygame.Surface((W, H))
        self.clock = pygame.time.Clock()
        self.fonts = {}
        self.campus_art = campus((W, H))
        self.menu_art = self.load_menu_art()
        self.menu_buttons = self.load_menu_buttons()
        self.school_logo = self.load_ui_image("logo.png")
        self.title_font = pygame.font.SysFont("consolas", 61, bold=True)
        self.maps = build_maps((W, H))
        self.room_obstacles = tuple(tuple(pygame.Rect(box) for box in boxes) for boxes in FURNITURE)
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
        self.role = "attack"
        self.room_index = 0
        self.talked = set()
        self.dialogue = []
        self.speaker = None
        self.skill_timer = self.dash_time = self.ally_timer = self.guard_clock = 0.0
        self.dash_direction = pygame.Vector2()
        self.combat_message = ""
        self.combat_message_timer = 0.0
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
        self.player_throw_time = self.boss_throw_time = 0.0
        self.throw_direction = pygame.Vector2(0, 1)
        self.speech_age = 0.0
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


    def font(self, size):
        if size not in self.fonts:
            self.fonts[size] = pygame.font.SysFont("arial", size, bold=False)
        return self.fonts[size]

    def tx(self, portuguese, english):
        values = self.settings_draft if getattr(self, "state", "") == "settings" else self.settings
        return english if values.get("language") == "en" else portuguese

    def difficulty_profile(self):
        profile = self.DIFFICULTIES[self.difficulty].copy()
        if self.room_index == 2:
            profile.update(speed=profile["speed"]*.8, rps_interval=2.6, rps_speed=245, rps_damage=10)
        elif self.room_index == 3:
            profile.update(hp=profile["hp"]+40, speed=profile["speed"]*.85, rps_interval=None)
        elif self.room_index == 4:
            profile.update(hp=profile["hp"]+60, rps_interval=3.4, rps_speed=285, rps_damage=12)
        return profile

    def player_hearts_for_difficulty(self):
        return 5 if self.difficulty in ("easy", "medium") else 3

    @property
    def room(self):
        return ROOMS[self.room_index]

    @property
    def guarding(self):
        return self.room_index in (3, 4) and self.guard_clock % 5 >= 3

    def nearest_resident(self):
        return min(enumerate(self.room.residents), key=lambda entry: self.player.distance_to(entry[1].position))

    def ready_to_leave(self):
        return all(index in self.talked for index, npc in enumerate(self.room.residents) if npc.required)

    def exit_is_open(self):
        return self.phase == "cleared" or (
            self.phase in ("explore", "intro") and not self.room.boss and self.ready_to_leave()
        )

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
                pygame.mixer.init(frequency=RATE, size=-16, channels=2, buffer=512)
            pygame.mixer.set_num_channels(8)
            self.music_channel = pygame.mixer.Channel(0)
            self.sfx_channel = pygame.mixer.Channel(1)
            self.voice_channel = pygame.mixer.Channel(2)
            self.music_tracks = {}
            self.victory_sound = pygame.mixer.Sound(buffer=self.make_victory_sound().tobytes())
            self.click_sound = pygame.mixer.Sound(buffer=self.make_tone((660,), .045, 5500, fade=True).tobytes())
            self.punch_sound = pygame.mixer.Sound(buffer=self.make_tone((125, 82), .12, 8500, fade=True).tobytes())
            self.hit_sound = pygame.mixer.Sound(buffer=self.make_tone((72, 108, 145), .18, 7600, fade=True).tobytes())
            self.block_sound = pygame.mixer.Sound(buffer=self.make_tone((310, 470), .09, 6500, fade=True).tobytes())
            self.throw_sound = pygame.mixer.Sound(buffer=self.make_tone((420, 735), .08, 3400, fade=True).tobytes())
            self.audio_ok = True
            self.current_music = None
            self.set_music()
            self.apply_audio(self.settings)
        except pygame.error:
            # Alguns dispositivos sem saída de áudio podem executar o jogo normalmente.
            self.audio_ok = False

    @staticmethod
    def make_tone(frequencies, duration, amplitude, fade=False):
        rate = RATE
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
        rate, note_duration = RATE, .14
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


    def apply_audio(self, settings):
        if self.audio_ok:
            master = float(settings["master"])
            self.music_channel.set_volume(master * float(settings["music"]))
            self.sfx_channel.set_volume(master * float(settings["sfx"]))
            self.voice_channel.set_volume(master * float(settings["sfx"]) * .8)

    def set_music(self):
        if not self.audio_ok:
            return
        index = self.room.chapter if self.state == "game" or self.settings_return_to_pause else 0
        if index not in self.music_tracks:
            self.music_tracks[index] = pygame.mixer.Sound(buffer=theme_pcm(index))
        sound = self.music_tracks[index]
        if self.current_music is sound and self.music_channel.get_busy():
            return
        self.music_channel.play(sound, loops=-1, fade_ms=280)
        self.current_music = sound

    def play_sfx(self, name="click"):
        if self.audio_ok:
            sound = {"punch": self.punch_sound, "hit": self.hit_sound,
                     "block": self.block_sound, "victory": self.victory_sound,
                     "throw": self.throw_sound}.get(name, self.click_sound)
            self.sfx_channel.play(sound)

    def play_dialogue_voice(self):
        self.speech_age = 0
        if self.audio_ok:
            name, line = self.current_dialogue()
            self.voice_channel.play(pygame.mixer.Sound(buffer=speech_pcm(line, name)))

    def stop_dialogue_voice(self):
        if self.audio_ok:
            self.voice_channel.stop()

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

    @staticmethod
    def heading(direction):
        if direction.y < -.45:
            return "up"
        if direction.y > .45:
            return "down"
        return "side"

    def place_sprite(self, name, point, scale, pose="idle", frame=0, facing="down", flip=False, hurt=False):
        source = sprite(name, facing, pose, frame)
        image = pygame.transform.scale_by(source, scale)
        if flip:
            image = pygame.transform.flip(image, True, False)
        if hurt:
            self.tint_damage(image)
        self.canvas.blit(image, (round(point[0]-image.get_width()/2), round(point[1]-38*scale)))

    @staticmethod
    def tint_damage(image):
        image.fill((255, 67, 79), special_flags=pygame.BLEND_RGB_MULT)
        image.fill((90, 0, 6), special_flags=pygame.BLEND_RGB_ADD)

    def panel(self, rect, color=(18, 24, 52, 235), border=CYAN, radius=12):
        surf = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(self.canvas, (15, 22, 34), rect.move(5, 6), border_radius=radius)
        pygame.draw.rect(surf, color, surf.get_rect(), border_radius=radius)
        pygame.draw.rect(surf, border, surf.get_rect(), 2, border_radius=radius)
        if rect.w > 200:
            for index, accent in enumerate(LOGO_COLORS):
                pygame.draw.rect(surf, accent, (10+index*12, 0, 10, 4))
        self.canvas.blit(surf, rect)

    def button(self, key, label, rect, *, font=22, accent=CYAN):
        mouse = pygame.mouse.get_pos()
        scale = pygame.Vector2(self.screen.get_size())
        mouse = (mouse[0] * W / max(scale.x, 1), mouse[1] * H / max(scale.y, 1))
        hovered = rect.collidepoint(mouse)
        color = tuple(round(channel*(.56 if hovered else .34)+16) for channel in accent)
        pygame.draw.rect(self.canvas, (15, 22, 34), rect.move(0, 4))
        pygame.draw.rect(self.canvas, color, rect)
        pygame.draw.rect(self.canvas, WHITE if hovered else accent, rect, 2)
        pygame.draw.rect(self.canvas, accent, (rect.left+3, rect.top+7, 3, rect.height-14))
        self.text(label, rect.center, font, WHITE, True)
        self.controls.append((key, rect))

    def draw_campus(self, overlay=0):
        self.canvas.blit(self.campus_art, (0, 0))
        if overlay:
            shade = pygame.Surface((W, H), pygame.SRCALPHA)
            shade.fill((16, 24, 43, overlay))
            self.canvas.blit(shade, (0, 0))

    @staticmethod
    def load_ui_image(filename):
        path = Path(__file__).resolve().parent / "assets" / "ui" / filename
        try:
            return pygame.image.load(str(path)).convert_alpha()
        except (pygame.error, FileNotFoundError):
            return None

    def load_menu_art(self):
        original = self.load_ui_image("ChatGPT Image 19 de ago. de 2026, 12_50_59.png")
        if original is None:
            return self.campus_art
        return pygame.transform.scale(pygame.transform.smoothscale(original, (320, 180)), (W, H))

    def load_menu_buttons(self):
        filenames = ("sheetbotao.png", "ChatGPT Image 19 de ago. de 2026, 14_30_45.png",
                     "ChatGPT Image 19 de ago. de 2026, 14_31_39.png")
        sheets = tuple(self.load_ui_image(path) for path in filenames)
        regions = (
            ((311, 10, 925, 254), (279, 11, 1007, 248), (270, 0, 1036, 259)),
            ((308, 268, 931, 252), (276, 266, 1003, 250), (270, 264, 1020, 254)),
            ((314, 523, 901, 248), (275, 522, 983, 252), (272, 523, 996, 249)),
            ((321, 780, 894, 230), (289, 779, 966, 232), (279, 775, 986, 241)),
        )
        return tuple(tuple(sheet.subsurface(region).copy() if sheet is not None else None
                           for sheet, region in zip(sheets, row)) for row in regions)

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
        self.set_music()

    def save_game(self):
        data = {
            "name": self.name, "gender": self.gender, "player_hp": self.player_hp,
            "difficulty": self.difficulty,
            "boss_hp": self.boss_hp, "player": [self.player.x, self.player.y],
            "boss": [self.boss.x, self.boss.y],
            "phase": {"intro": "explore", "won": "verdict"}.get(self.phase, self.phase),
            "campaign_version": 3, "room": self.room_index, "role": self.role, "talked": sorted(self.talked),
            "skill_timer": self.skill_timer, "paper_cooldown": self.paper_cooldown,
        }
        try:
            pending = self.save_path.with_suffix(".tmp")
            pending.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            pending.replace(self.save_path)
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
            room_index = data.get("room", 1)
            if not isinstance(room_index, int) or not 0 <= room_index < len(ROOMS):
                return False
            role = "sprinter" if data.get("role") == "support" else data.get("role")
            self.role = role if role in ROLES else "attack"
            self.enter_room(room_index)
            saved_player_hp = int(data.get("player_hp", self.player_hp_max))
            # Converte saves antigos que guardavam vida de 0 a 100 para corações.
            if saved_player_hp > self.player_hp_max:
                saved_player_hp = math.ceil(saved_player_hp / 100 * self.player_hp_max)
            self.player_hp = max(1, min(self.player_hp_max, saved_player_hp))
            self.boss_hp = max(1, min(self.boss_hp_max, int(data.get("boss_hp", self.boss_hp_max))))
            version = data.get("campaign_version")
            current_map = version in (2, 3)
            if current_map:
                self.player.update(*data.get("player", [640, 540]))
                self.boss.update(*data.get("boss", [640, 288]))
            else:
                self.boss.update(640, 320)
            phase = data.get("phase")
            self.phase = phase if self.room.boss and phase in ("combat", "cleared", "verdict") else "explore"
            if self.phase in ("cleared", "verdict"):
                self.boss_hp = 0
                if self.phase == "verdict" or version != 3:
                    self.show_verdict()
            if current_map:
                self.talked = {i for i in data.get("talked", []) if isinstance(i, int) and 0 <= i < len(self.room.residents)}
            self.saved_prompt = False
            self.player_action = self.boss_action = "idle"
            self.player_hurt_timer = self.boss_hurt_timer = self.impact_timer = 0.0
            self.player_moving = self.boss_moving = False
            self.walk_anim_time = self.boss_anim_time = 0.0
            self.attack_timer = self.boss_attack_timer = 0.0
            self.rps_attack_timer = 0.0
            self.projectiles.clear()
            self.paper_projectiles.clear()
            self.paper_cooldown = max(0.0, min(5.0, float(data.get("paper_cooldown", 0))))
            self.skill_timer = max(0.0, min(ROLES[self.role].cooldown, float(data.get("skill_timer", 0))))
            self.player_blocking = False
            self.block_keys_down.clear()
            self.block_press_consumed = False
            self.set_state("game")
            return True
        except (OSError, ValueError, TypeError, json.JSONDecodeError):
            return False

    def start_game(self):
        self.enter_room(0)

    def enter_room(self, room_index):
        self.room_index = room_index
        self.talked.clear()
        self.dialogue = []
        self.speaker = None
        self.player.update(105, self.DOORWAY.centery)
        self.boss.update(640, 160)
        self.direction.update(1, 0)
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
        self.attack_flash = 0.0
        self.player_blocking = False
        self.block_keys_down.clear()
        self.block_press_consumed = False
        self.block_flash = 0.0
        self.player_throw_time = self.boss_throw_time = 0.0
        self.stop_dialogue_voice()
        self.rps_attack_timer = 0.0
        self.projectiles.clear()
        self.paper_projectiles.clear()
        self.paper_cooldown = 0.0
        self.skill_timer = self.dash_time = self.guard_clock = 0.0
        self.ally_timer = 5.0
        self.combat_message = ""
        self.combat_message_timer = 0.0
        self.paused = False
        self.dialogue_step, self.phase = 0, "explore"
        self.attack_timer = self.boss_attack_timer = 0.0
        self.set_state("game")

    def interact(self):
        if self.phase != "explore":
            return
        index, npc = self.nearest_resident()
        if self.player.distance_to(npc.position) <= 100:
            self.speaker = index
            self.dialogue = npc.lines
            self.dialogue_step = 0
            self.phase = "intro"
            self.play_dialogue_voice()

    def check_passage(self):
        if self.DOORWAY.collidepoint(self.player) and self.exit_is_open():
            if self.room_index+1 < len(ROOMS):
                self.enter_room(self.room_index+1)
            else:
                self.finish_campaign()
        elif (self.phase == "explore" and self.room.boss
              and self.ARENA.collidepoint(self.player) and self.ready_to_leave()):
            self.begin_combat()

    def show_verdict(self):
        self.speaker = next(index for index, npc in enumerate(self.room.residents) if npc.outfit == "rival")
        self.dialogue = [VERDICTS[self.room_index]]
        self.dialogue_step = 0
        self.phase = "verdict"
        self.play_dialogue_voice()

    def finish_campaign(self):
        try:
            self.save_path.unlink(missing_ok=True)
        except OSError:
            pass
        self.set_state("victory")

    def render_loading(self):
        self.draw_campus(130)
        self.panel(pygame.Rect(305, 154, 670, 445), (21, 38, 54, 248), GOLD)
        self.draw_game_title(640, 225)
        for index, name in enumerate(("Levi", "Reidryan", "Bruno", "Davi", "Jaylson", "Jota")):
            self.place_sprite(name, (445+index*78, 464), 2, "walk", int(self.progress/5+index)%4)
        if self.progress < 100:
            self.load_tick += self.state_time
            if self.load_tick > .04:
                self.progress = min(100, self.progress + random.uniform(2.5, 7))
                self.load_tick = 0.0
        self.state_time = 0.0
        step = min(int(self.progress // 20), 4)
        labels = [self.tx("Preparando a escola", "Preparing the school"),
                  self.tx("Montando os cenários", "Setting up the rooms"),
                  self.tx("Reunindo os Atiçadores", "Gathering the team"),
                  self.tx("Ajustando a música", "Setting up the music"),
                  self.tx("Quase pronto", "Almost ready")]
        self.text(self.tx("Pronto!", "Ready!") if self.progress >= 100 else labels[step], (W//2, 515), 20, WHITE, True)
        self.draw_bar(pygame.Rect(377, 549, 526, 20), self.progress, 100, CYAN)

    def draw_game_title(self, x, y):
        shadow = self.title_font.render("ATIÇADORES", False, (9, 23, 35))
        title = self.title_font.render("ATIÇADORES", False, GOLD)
        self.canvas.blit(shadow, shadow.get_rect(center=(x+4, y+5)))
        self.canvas.blit(title, title.get_rect(center=(x, y)))
        self.text("L T D A", (x, y+55), 24, CYAN, True)

    def render_menu(self):
        self.canvas.blit(self.menu_art, (0, 0))
        self.panel(pygame.Rect(64, 66, 388, 544), (19, 34, 49, 225), (143, 184, 172), 4)
        self.draw_game_title(258, 133)
        self.text(self.tx("A resenha contra-ataca", "The school crew strikes back"), (258, 231), 19, WHITE, True)
        labels = (("play", "JOGAR", "PLAY", LOGO_COLORS[4]), ("options", "OPÇÕES", "OPTIONS", LOGO_COLORS[1]),
                  ("credits", "CRÉDITOS", "CREDITS", LOGO_COLORS[2]), ("quit", "SAIR", "QUIT", LOGO_COLORS[3]))
        sx, sy = self.screen.get_size()
        mx, my = pygame.mouse.get_pos()
        mouse = (mx*W/max(1, sx), my*H/max(1, sy))
        for index, (key, pt, en, accent) in enumerate(labels):
            rect = pygame.Rect(85, 257+index*86, 346, 88)
            over = rect.collidepoint(mouse) and not (self.credits or self.saved_prompt)
            state = 2 if over and pygame.mouse.get_pressed()[0] else int(over)
            art = self.menu_buttons[index][state]
            if self.settings["language"] == "pt_BR" and art is not None:
                self.canvas.blit(pygame.transform.scale(art, rect.size), rect)
                self.controls.append((key, rect))
            else:
                self.button(key, self.tx(pt, en), rect.inflate(-8, -16), font=24, accent=accent)
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
        self.draw_campus(118)
        self.button("back", self.tx("← VOLTAR", "← BACK"), pygame.Rect(18, 18, 145, 46), font=18)
        self.panel(pygame.Rect(250, 66, 780, 624), (14, 20, 47, 235))
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
        self.panel(pygame.Rect(545, 263, 190, 171), (36, 67, 84, 255), (111, 184, 169), 4)
        pygame.draw.ellipse(self.canvas, (22, 41, 59), (601, 412, 78, 14))
        pose = "wave" if self.state_time%3.8 < .38 else "idle"
        self.place_sprite(gender, (640, 420), 4, pose)
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
        for index, (key, role) in enumerate(ROLES.items()):
            rect = pygame.Rect(355+index*195, 563, 180, 36)
            self.button("role_"+key, self.tx(*role.title), rect, font=17, accent=role.color)
            if key == self.role:
                pygame.draw.rect(self.canvas, role.color, rect, 3, border_radius=8)
        self.text(self.tx(*ROLES[self.role].description), (640, 616), 16, ROLES[self.role].color, True)
        self.button("confirm", self.tx("COMEÇAR", "START"), pygame.Rect(560, 638, 160, 40),
                    font=20, accent=LOGO_COLORS[0])

    def render_settings(self):
        values = self.settings_draft
        self.draw_campus(150)
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
        self.button("clear_save", self.tx("EXCLUIR DADOS SALVOS", "CLEAR SAVED SETTINGS"),
                    pygame.Rect(740, 280, 270, 45), font=16, accent=LOGO_COLORS[3])
        if self.school_logo is not None:
            self.canvas.blit(pygame.transform.scale(self.school_logo, (144, 144)), (804, 405))
        if self.feedback:
            self.text(self.feedback, (740, 350), 16, (100, 240, 150))
        cancel_label = self.tx("VOLTAR À PAUSA", "BACK TO PAUSE") if self.settings_return_to_pause else self.tx("CANCELAR", "CANCEL")
        self.button("cancel_settings", cancel_label, pygame.Rect(710, 600, 155, 46), font=17)
        self.button("save_settings", self.tx("SALVAR", "SAVE"), pygame.Rect(880, 600, 130, 46),
                    font=17, accent=LOGO_COLORS[2])

    def render_pause(self):
        shade = pygame.Surface((W, H), pygame.SRCALPHA)
        shade.fill((0, 0, 0, 175))
        self.canvas.blit(shade, (0, 0))
        self.panel(pygame.Rect(390, 170, 500, 390), (15, 22, 48, 250), GOLD)
        self.text(self.tx("PAUSADO", "PAUSED"), (640, 225), 36, GOLD, True)
        self.button("pause_resume", self.tx("RETORNAR AO JOGO", "RESUME GAME"),
                    pygame.Rect(505, 290, 270, 55), font=20, accent=LOGO_COLORS[2])
        self.button("pause_settings", self.tx("CONFIGURAÇÕES", "SETTINGS"), pygame.Rect(505, 370, 270, 55), font=20)
        self.button("pause_save_exit", self.tx("SALVAR E SAIR", "SAVE AND EXIT"),
                    pygame.Rect(505, 450, 270, 55), font=20, accent=LOGO_COLORS[4])
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


    def move_with_room_collision(self, position, movement, radius=12):
        """Move an actor along each axis so it can slide around furniture."""
        obstacles = self.room_obstacles[self.room_index]
        if self.room_index == 0:
            obstacles = [pygame.Rect(x+31, y+42, 48, 25) for x, y in CLASSROOM_DESKS]
        for axis in ("x", "y"):
            candidate = position.copy()
            setattr(candidate, axis, getattr(candidate, axis)+getattr(movement, axis))
            at_open_door = (
                self.exit_is_open() and self.DOORWAY.top+radius <= candidate.y < self.DOORWAY.bottom-radius
            )
            right_edge = W-25 if at_open_door else self.DOORWAY.left-radius
            candidate.x = max(48, min(right_edge, candidate.x))
            candidate.y = max(250 if self.room_index == 3 else 230 if self.room_index else 110, min(H-58, candidate.y))
            feet_box = pygame.Rect(round(candidate.x-radius), round(candidate.y-radius),
                                   radius*2, radius*2)
            if not any(feet_box.colliderect(obstacle) for obstacle in obstacles):
                setattr(position, axis, getattr(candidate, axis))

    def render_game(self):
        self.canvas.blit(self.maps[self.room_index], (0, 0))
        if self.room_index in (0, 5):
            color = (212, 173, 116) if self.room_index == 0 else (225, 215, 161)
            for i in range(14):
                x = 72+(i*147+round(self.state_time*(6+i%4)))%1136
                y = 261+(i*87+round(6*math.sin(self.state_time+i)))%352
                pygame.draw.rect(self.canvas, color, (x, y, 3, 2))
        pygame.draw.rect(self.canvas, (21, 26, 44), (340, 6, 600, 66))
        self.text(f"{self.room.chapter:02d}  •  {self.tx(*CHAPTERS[self.room.chapter-1])}", (640, 22), 16, CYAN, True)
        self.text(self.tx(*self.room.name), (640, 48), 24, WHITE, True)
        pygame.draw.rect(self.canvas, self.room.color, (36, 95, W-72, 18))
        self.draw_school_details()
        exploring = self.phase in ("explore", "intro", "cleared")
        self.draw_doorways()
        if self.phase == "explore" and self.room.boss and self.ready_to_leave():
            pygame.draw.rect(self.canvas, GOLD, self.ARENA, 2, border_radius=8)
        self.draw_projectiles()
        actors = [(self.player.y, "player", None)]
        if not exploring and self.room.boss:
            actors.append((self.boss.y, "boss", None))
            title = self.tx(*self.room.boss)
            if self.phase == "combat" and self.guarding:
                title += self.tx("  •  Guarda", "  •  Guard")
            self.text(f"{title}   {self.boss_hp}/{self.boss_hp_max}", (640, 84), 15, (255, 170, 170), True)
            self.draw_bar(pygame.Rect(390, 98, 500, 12), self.boss_hp, self.boss_hp_max, (205, 55, 55))
        for index, npc in enumerate(self.room.residents):
            if exploring or npc.outfit != "rival":
                actors.append((npc.position[1], "npc", index))
        for _, kind, index in sorted(actors, key=lambda actor: actor[0]):
            if kind == "npc":
                self.draw_resident(index)
            else:
                self.draw_person(self.player if kind == "player" else self.boss, kind)
        if self.phase == "combat":
            self.draw_team_status()
        self.text(f"{self.tx('Dificuldade', 'Difficulty')}: {self.difficulty_name()}", (120, 78), 14, GOLD, True)
        goal = self.tx("Recuperar a resenha", "Bring back the good times")
        if self.room_index == len(ROOMS)-1:
            goal = self.tx("A resenha voltou!", "The good times are back!")
        self.text(goal, (1100, 78), 17, GOLD, True)
        role = ROLES[self.role]
        pygame.draw.rect(self.canvas, (25, 35, 51), (0, 679, W, 41))
        for i, accent in enumerate(LOGO_COLORS):
            pygame.draw.rect(self.canvas, accent, (i*(W//5), 679, W//5, 3))
        self.text(f"{self.name}  ·  {self.tx(*role.title)}", (640, 634), 16, role.color, True)
        self.draw_player_hearts()
        if self.phase in ("explore", "cleared"):
            _, npc = self.nearest_resident()
            if self.exit_is_open():
                hint = self.tx("Atravesse a porta aberta à direita.", "Walk through the open door on the right.")
            elif self.room.boss and self.ready_to_leave():
                hint = self.tx("Entre na área marcada para começar o desafio.", "Walk into the marked area to start the challenge.")
            elif self.player.distance_to(npc.position) <= 100:
                hint = self.tx("E  ·  Conversar com ", "E  ·  Talk to ") + self.tx(*npc.name).split(" • ")[0]
            else:
                hint = self.tx("WASD / setas para andar  •  Fale com quem tem !", "WASD / arrows to move  •  Talk to characters marked !")
            if self.role == "sprinter":
                status = f" ({math.ceil(self.skill_timer)}s)" if self.skill_timer > 0 else ""
                hint += f"   |   Q · Dash{status}"
            self.text(hint, (640, 693), 17, WHITE, True)
        elif self.phase == "combat":
            status = f"{math.ceil(self.skill_timer)}s" if self.skill_timer > 0 else self.tx("pronto", "ready")
            hint = self.tx("Espaço/Z · Soco   |   Mouse · Papel   |   C/Shift · Defesa",
                           "Space/Z · Punch   |   Mouse · Paper   |   C/Shift · Block")
            self.text(f"{hint}   |   Q · {self.tx(*role.skill)} ({status})", (640, 693), 17, WHITE, True)
            if self.combat_message_timer > 0:
                self.text(self.combat_message, (640, 605), 18, role.color, True)
        if self.phase in ("intro", "verdict"):
            self.draw_dialogue()
        if self.phase == "lost":
            self.render_death_popup()

    def draw_doorways(self):
        y = self.DOORWAY.top
        opened = self.exit_is_open()
        frame = (36, 28, 44)
        pygame.draw.rect(self.canvas, frame, (0, y-5, 45, 98))
        pygame.draw.rect(self.canvas, (40, 73, 85), (0, y, 38, 88))
        pygame.draw.rect(self.canvas, (115, 197, 179), (0, y+69, 38, 16))
        pygame.draw.rect(self.canvas, frame, (1210, y-5, 70, 98))
        if opened:
            pygame.draw.rect(self.canvas, (40, 73, 85), (1217, y, 63, 88))
            pygame.draw.polygon(self.canvas, (115, 197, 179), ((1217, y+67), (1280, y+67),
                                                               (1280, y+88), (1217, y+88)))
            pygame.draw.lines(self.canvas, WHITE, False, ((1244, y+31), (1255, y+43), (1244, y+55)), 3)
        else:
            pygame.draw.rect(self.canvas, (113, 74, 79), (1217, y, 55, 88))
            pygame.draw.rect(self.canvas, (158, 104, 102), (1222, y+5, 45, 73), 2)
            pygame.draw.circle(self.canvas, GOLD, (1229, y+46), 4)
        if self.room_index+1 < len(ROOMS):
            label = self.tx(*ROOMS[self.room_index+1].name)
        else:
            label = self.tx("Fim do intervalo", "End of break")
        self.text(label, (1183, y-19), 15, CYAN if opened else WHITE, True)

    def draw_team_status(self):
        self.panel(pygame.Rect(50, 545, 255, 54), (20, 26, 42, 240), CYAN, 6)
        self.text(self.tx("Cobertura de Davi e Jaylson", "Davi and Jaylson's cover"), (177, 564), 16, CYAN, True)
        self.draw_bar(pygame.Rect(73, 583, 209, 6), self.ally_timer, 6, CYAN)

    def draw_school_details(self):
        labels = (("Mural de avisos", "Notice board"), ("Armários", "Lockers"),
                  ("Balcão de refeições", "Lunch counter"), ("Palco", "Stage"),
                  ("Quadro de horários", "Schedule board"), ("Pátio das turmas", "School courtyard"))
        self.panel(pygame.Rect(955, 114, 260, 34), (24, 30, 45, 245), self.room.color, 4)
        self.text(self.tx(*labels[self.room_index]), (1085, 131), 16, WHITE, True)

    def draw_resident(self, index):
        npc = self.room.residents[index]
        name = npc.name[0].split(" • ")[0]
        x, y = npc.position
        pending = (self.phase in ("explore", "intro") and npc.required
                   and index not in self.talked and index != self.speaker)
        cycle = (self.state_time+index*.27) % 2.8
        lift = round(5*math.sin(cycle*math.pi/.6)) if pending and cycle < .6 else 0
        pygame.draw.ellipse(self.canvas, (51, 51, 60), (x-18, y-5, 36, 10))
        speaking = index == self.speaker and self.speech_age < 2.4 and int(self.speech_age*12)%2 == 0
        pose = "talk" if speaking else "wave" if pending and cycle < .6 else "blink" if cycle > 2.64 else "idle"
        self.place_sprite(name, (x, y-lift), 2, pose)
        self.text(self.tx(*npc.name), (x+1, y-86-lift), 16, (24, 28, 40), True)
        self.text(self.tx(*npc.name), (x, y-88-lift), 16, WHITE, True)
        if pending:
            bubble = pygame.Rect(x-11, y-123-lift, 22, 21)
            pygame.draw.rect(self.canvas, (32, 45, 61), bubble, border_radius=3)
            pygame.draw.rect(self.canvas, GOLD, bubble, 2, border_radius=3)
            self.text("!", bubble.center, 16, GOLD, True)

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
        self.text(self.tx("FIM DA RODADA", "ROUND LOST"), (640, panel_rect.y+72), 40, (255, 105, 105), True)
        self.text(self.tx("A batalha foi perdida.", "The battle is over."), (640, panel_rect.y+125), 20, (225, 220, 220), True)
        if progress >= .65:
            button_y = panel_rect.y + 177
            self.button("retry_death", self.tx("TENTAR NOVAMENTE", "TRY AGAIN"), pygame.Rect(475, button_y, 330, 48), font=18)
            self.button("menu_death", self.tx("VOLTAR AO MENU PRINCIPAL", "BACK TO MAIN MENU"), pygame.Rect(475, button_y+62, 330, 48), font=17)

    def draw_person(self, pos, kind):
        x, y = round(pos.x), round(pos.y)
        pygame.draw.ellipse(self.canvas, (48, 45, 55), (x-23, y-5, 46, 11))
        if kind == "boss":
            name = self.BOSS_STYLES[self.room_index-1]
            scale = 2 if name == "Bia" else 3
            facing = self.heading(self.boss_direction)
            if self.boss_action == "attack":
                pose, frame = "punch", int(self.boss_action_time >= .25)
            elif self.boss_action == "hurt":
                pose, frame = "hurt", 0
            elif self.boss_throw_time > 0:
                pose, frame = "throw", int(self.boss_throw_time < .16)
            else:
                pose = "walk" if self.boss_moving else "idle"
                frame = int(self.boss_anim_time*7)%4
            recoil = round(7*self.boss_hurt_timer/.30)
            self.place_sprite(name, (x-self.boss_direction.x*recoil, y-recoil//2),
                              scale, pose, frame, facing, facing == "side" and self.boss_direction.x < 0,
                              hurt=self.attack_flash > 0 or self.boss_hurt_timer > .12)
            if self.phase == "combat" and self.boss_action == "attack" and not self.boss_action_hit:
                self.text("!", (x, y-scale*39-12), 25, GOLD, True)
            elif self.phase == "combat" and self.guarding:
                pygame.draw.ellipse(self.canvas, (173, 219, 224), (x-37, y-91, 74, 92), 2)
        else:
            throwing = self.player_throw_time > 0 and self.player_action != "hurt"
            direction = self.direction
            if self.player_action == "punch":
                direction = self.player_action_direction
            if throwing:
                direction = self.throw_direction
            facing = self.heading(direction)
            flip = facing == "side" and direction.x < 0
            if self.phase == "lost":
                fallen = pygame.transform.scale_by(sprite(self.gender, facing, "hurt"), 2)
                if self.state_time < .22:
                    self.tint_damage(fallen)
                fallen = pygame.transform.rotate(fallen, min(90, self.state_time*180))
                self.canvas.blit(fallen, fallen.get_rect(center=(x, y-20)))
                return
            if self.dash_time > 0:
                for index in (3, 2, 1):
                    tx, ty = pos-self.dash_direction*(index*16)
                    pygame.draw.rect(self.canvas, (87+index*19, 183, 188), (tx-13, ty-7, 26, 3))
                pose, frame = "dash", 0
            elif self.player_blocking or self.block_flash > 0:
                pose, frame = "block", int(self.block_flash > .10)
            elif throwing:
                pose, frame = "throw", int(self.player_throw_time < .17)
            elif self.player_action in ("punch", "hurt"):
                pose, frame = self.player_action, int(self.player_action_time >= .13)
            else:
                pose = "walk" if self.player_moving else "blink" if self.state_time%4 > 3.84 else "idle"
                frame = int(self.walk_anim_time*9)%4
            recoil = round(8*self.player_hurt_timer/.34)
            self.place_sprite(self.gender, (x+recoil*(1 if flip else -1), y-recoil//2),
                              2, pose, frame, facing, flip, hurt=self.player_hurt_timer > .12)
            if self.player_blocking or self.block_flash > 0:
                pygame.draw.arc(self.canvas, CYAN, (x-37, y-75, 74, 78), -.42, 3.58, 3)
            self.text(self.name, (x, y-87), 14, WHITE, True)
        if self.impact_timer > 0 and pos.distance_to(self.impact_position) < 1:
            self.draw_impact(x, y-45, kind == "player" and self.block_flash > 0)

    def draw_projectiles(self):
        for shots, default in ((self.projectiles, "paper"), (self.paper_projectiles, "ball")):
            for shot in shots:
                center = shot["pos"]
                direction = shot["velocity"].normalize() if shot["velocity"] else pygame.Vector2()
                for i in range(1, 4):
                    streak = center-direction*(i*7)
                    pygame.draw.rect(self.canvas, (238, 217, 167), (streak.x-2, streak.y-1, 4, 2))
                image = projectile(shot.get("kind", default), int(self.state_time*18)%8)
                self.canvas.blit(image, image.get_rect(center=center))

    def throw_paper(self, aim_point):
        if (self.state != "game" or self.paused or self.phase != "combat"
                or self.paper_cooldown > 0 or self.player_blocking or self.player_action == "hurt"):
            return
        origin = self.player + pygame.Vector2(0, -48)
        target = pygame.Vector2(aim_point)
        direction = target-origin
        if not direction.length_squared(): direction = self.direction.copy()
        if not direction.length_squared(): direction = pygame.Vector2(0, -1)
        direction = direction.normalize()
        self.paper_projectiles.append({"pos": origin, "velocity": direction*520})
        self.paper_cooldown = 5.0
        self.throw_direction = direction
        self.player_throw_time = .24
        self.play_sfx("throw")

    def spawn_rps_projectile(self, profile):
        kind = random.choice(("rock", "paper", "scissors"))
        direction = self.player - self.boss
        if not direction.length_squared(): direction = pygame.Vector2(-1, 0)
        direction = direction.normalize()
        self.projectiles.append({"pos": self.boss.copy(), "velocity": direction*profile["rps_speed"],
                                 "kind": kind, "damage": profile["rps_damage"]})
        self.boss_throw_time = .28
        self.play_sfx("throw")

    def draw_impact(self, x, y, blocked=False):
        color = CYAN if blocked else (255, 180, 110)
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
        npc = self.room.residents[self.speaker]
        name = npc.name[0].split(" • ")[0]
        self.panel(pygame.Rect(101, 535, 121, 147), (31, 55, 65, 255), CYAN, 4)
        pose = "talk" if self.speech_age < 2.4 and int(self.speech_age*12)%2 == 0 else "idle"
        self.place_sprite(name, (161, 667), 3, pose)
        self.text(speaker, (249, 537), 22, GOLD)
        self.wrapped(content, pygame.Rect(249, 578, 905, 86), 20)
        self.text(self.tx("Espaço / Enter / E · Continuar", "Space / Enter / E · Continue"), (1010, 675), 15, (175, 175, 180), True)

    def current_dialogue(self):
        npc = self.room.residents[self.speaker]
        return self.tx(*npc.name), self.tx(*self.dialogue[self.dialogue_step]).replace("{name}", self.name)

    def render_victory(self):
        self.draw_campus(84)
        self.panel(pygame.Rect(223, 79, 834, 558), (23, 42, 56, 242), GOLD)
        self.text(self.tx("A RESENHA VOLTOU!", "THE GOOD TIMES ARE BACK!"), (640, 145), 49, GOLD, True)
        self.text(self.tx(f"{self.name} reuniu as turmas no pátio.", f"{self.name} brought the groups together in the courtyard."), (640, 224), 24, WHITE, True)
        for index, name in enumerate(("Levi", "Davi", self.gender, "Jaylson", "Bruno")):
            y = 435-abs(round(7*math.sin(self.state_time*4+index*.55)))
            self.place_sprite(name, (425+index*107, y), 3, "wave")
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
        scaled = pygame.transform.scale(self.canvas, (sw, sh))
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
            for role in ROLES:
                if self.hit("role_"+role, p):
                    self.role = role
                    return
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
                if self.hit("retry_death", p):
                    self.enter_room(self.room_index)
                    self.begin_combat()
                elif self.hit("menu_death", p): self.paused = False; self.set_state("menu")
            elif self.paused:
                if self.hit("pause_resume", p): self.paused = False
                elif self.hit("pause_settings", p):
                    self.settings_return_to_pause = True
                    self.settings_draft = self.settings.copy()
                    self.set_state("settings")
                elif self.hit("pause_save_exit", p):
                    if self.save_game(): self.paused = False; self.saved_prompt = False; self.set_state("menu")
                    else: self.feedback = self.tx("Não foi possível salvar a partida.", "Could not save the game.")
            elif self.phase in ("intro", "verdict"): self.advance_dialogue()
        elif self.state == "victory":
            if self.hit("play_again", p): self.name_edit = self.name; self.set_state("select")
            elif self.hit("main_menu", p): self.set_state("menu")

    def set_slider(self, key, x):
        track_left, track_width = 465, 250
        self.settings_draft[key] = min(1, max(0, (x-track_left)/track_width))

    def advance_dialogue(self):
        self.dialogue_step += 1
        if self.dialogue_step < len(self.dialogue):
            self.play_dialogue_voice()
            return
        self.stop_dialogue_voice()
        if self.phase == "verdict":
            self.phase = "cleared"
            self.speaker = None
        else:
            self.talked.add(self.speaker)
            self.phase = "explore"
            self.speaker = None

    def begin_combat(self):
        self.phase = "combat"
        self.player.update(640, 540)
        self.direction.update(0, -1)
        self.boss.update(640, 320)
        self.dash_time = 0

    @staticmethod
    def movement_input():
        keys = pygame.key.get_pressed()
        return pygame.Vector2(
            int(keys[pygame.K_d] or keys[pygame.K_RIGHT])-int(keys[pygame.K_a] or keys[pygame.K_LEFT]),
            int(keys[pygame.K_s] or keys[pygame.K_DOWN])-int(keys[pygame.K_w] or keys[pygame.K_UP]),
        )

    def update_game(self, dt):
        self.speech_age += dt
        self.player_throw_time = max(0.0, self.player_throw_time-dt)
        self.boss_throw_time = max(0.0, self.boss_throw_time-dt)
        if self.phase == "lost":
            return
        self.boss_hurt_timer = max(0.0, self.boss_hurt_timer-dt)
        self.attack_flash = max(0.0, self.attack_flash-dt)
        self.impact_timer = max(0.0, self.impact_timer-dt)
        if self.phase == "won":
            if self.state_time > .7: self.show_verdict()
            return
        if self.phase not in ("explore", "cleared", "combat"):
            return
        self.block_flash = max(0.0, self.block_flash-dt)
        self.skill_timer = max(0.0, self.skill_timer-dt)
        move = self.movement_input()
        if self.dash_time > 0:
            duration = min(dt, self.dash_time)
            distance = 650*duration
            steps = max(1, math.ceil(distance/8))
            previous_player = self.player.copy()
            for _ in range(steps):
                self.move_with_room_collision(self.player, self.dash_direction*(distance/steps))
            self.player_moving = self.player.distance_to(previous_player) > .05
            self.dash_time = max(0.0, self.dash_time-dt) if self.player_moving else 0.0
        elif move.length_squared():
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
        if self.phase != "combat":
            self.check_passage()
            return

        self.paper_cooldown = max(0.0, self.paper_cooldown-dt)
        self.combat_message_timer = max(0.0, self.combat_message_timer-dt)
        self.guard_clock += dt
        self.ally_timer -= dt
        if self.ally_timer <= 0:
            self.ally_timer = 6.0
            self.damage_boss(8, assist=True)
            self.announce_combat(self.tx("Cobertura dos Atiçadores!", "Atiçadores cover fire!"))
            if self.phase != "combat":
                return
        self.attack_timer = max(0.0, self.attack_timer-dt)
        self.player_hurt_timer = max(0.0, self.player_hurt_timer-dt)
        profile = self.difficulty_profile()
        if self.player_action == "punch":
            self.player_action_time += dt
            if self.player_action_time >= .13 and not self.player_action_hit:
                self.player_action_hit = True
                target = self.player + self.player_action_direction*44
                if self.boss.distance_to(target) <= 62:
                    self.damage_boss(20)
                    if self.phase != "combat":
                        return
            if self.player_action_time >= .38:
                self.player_action = "idle"
        elif self.player_action == "hurt":
            self.player_action_time += dt
            if self.player_action_time >= .34: self.player_action = "idle"

        diff = self.player - self.boss
        if diff.length_squared(): self.boss_direction = diff.normalize()
        old_boss = self.boss.copy()
        ranged_gap = self.room_index == 2 and diff.length() < 165
        if diff.length_squared() and not ranged_gap and self.boss_action != "attack":
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
                if self.phase != "combat":
                    return
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
                self.projectiles.remove(shot)
                self.damage_player(shot["damage"])
                if self.phase != "combat":
                    return
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
        if self.phase != "combat" or self.player_hp <= 0: return
        if self.player_blocking:
            self.player_blocking = False
            self.block_press_consumed = True
            self.block_flash = .22
            self.play_sfx("block")
            self.impact_position = self.player.copy()
            self.impact_timer = .14
            return
        self.dash_time = 0.0
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

    def damage_boss(self, amount, *, break_guard=False, assist=False):
        if self.phase != "combat" or self.boss_hp <= 0: return
        if self.guarding and not break_guard:
            self.boss_hp = max(1, self.boss_hp-max(1, amount//4))
            if not assist:
                self.announce_combat(self.tx("Guarda ativa! Espere a abertura.", "Guard up! Wait for an opening."))
            return
        if break_guard and self.guarding:
            self.guard_clock = 0.0
        self.boss_hp = max(0, self.boss_hp-amount)
        if not assist:
            if self.boss_action != "attack" or break_guard:
                self.boss_action = "hurt"
                self.boss_action_time = 0.0
                self.boss_action_hit = False
            self.boss_hurt_timer = .30
        self.attack_flash = .18
        self.play_sfx("hit")
        self.impact_position = self.boss.copy()
        self.impact_timer = .18
        if self.boss_hp <= 0:
            self.finish_combat()

    def finish_combat(self):
        self.phase = "won"
        self.state_time = 0
        self.player_action = "idle"
        self.player_action_time = self.player_hurt_timer = self.player_throw_time = 0.0
        self.player_action_hit = False
        self.player_blocking = self.block_press_consumed = False
        self.block_keys_down.clear()
        self.block_flash = self.dash_time = 0.0
        self.player_moving = self.boss_moving = False
        self.walk_anim_time = 0.0
        self.boss_action = "hurt"
        self.boss_throw_time = 0.0
        self.projectiles.clear()
        self.paper_projectiles.clear()
        self.play_sfx("victory")

    def announce_combat(self, message):
        self.combat_message = message
        self.combat_message_timer = 1.2

    def use_role_skill(self):
        can_dash = self.role == "sprinter" and self.phase in ("explore", "cleared", "combat")
        if (self.phase != "combat" and not can_dash) or self.skill_timer > 0 or self.player_action == "hurt":
            return
        if self.role == "attack":
            if self.player.distance_to(self.boss) > 115:
                self.announce_combat(self.tx("Aproxime-se para usar Ruptura.", "Move closer to use Breakthrough."))
                return
            self.damage_boss(55, break_guard=True)
        elif can_dash:
            move = self.movement_input()
            self.dash_direction = move.normalize() if move.length_squared() else self.direction.copy()
            self.direction = self.dash_direction.copy()
            self.dash_time = .24
            self.player_blocking = False
        else:
            if self.player_hp == self.player_hp_max:
                self.announce_combat(self.tx("Seus corações já estão cheios.", "Your hearts are already full."))
                return
            self.player_hp = min(self.player_hp_max, self.player_hp+2)
        role = ROLES[self.role]
        self.skill_timer = role.cooldown
        self.announce_combat(self.tx(*role.skill))

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
        if self.phase == "combat" and self.player_action != "hurt" and not self.block_press_consumed:
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
                        if self.state == "game" and self.phase == "lost": self.set_state("menu")
                        elif self.state == "game":
                            self.paused = not self.paused
                            if self.paused:
                                self.stop_dialogue_voice()
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
                            if self.phase in ("intro", "verdict") and event.key in (pygame.K_e, pygame.K_SPACE, pygame.K_RETURN, pygame.K_KP_ENTER): self.advance_dialogue()
                            elif self.phase == "explore" and event.key == pygame.K_e: self.interact()
                            elif event.key == pygame.K_q and not getattr(event, "repeat", False): self.use_role_skill()
                            elif block_key and not getattr(event, "repeat", False):
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
