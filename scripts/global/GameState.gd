## GameState.gd — Autoload singleton
## Persiste dados do jogador e configuracoes entre cenas.
extends Node

# ── Dados do jogador ──────────────────────────────────────────
var player_name: String = "Jogador"
var player_gender: String = "boy"  # "boy" | "girl"

# ── Configuracoes ─────────────────────────────────────────────
var master_volume: float = 0.8
var sfx_volume: float = 0.8
var music_volume: float = 0.6
var brightness: float = 0.7
var fullscreen: bool = false
var language: String = "pt_BR"

# ── Persistencia ─────────────────────────────────────────────
const SETTINGS_PATH := "user://settings.cfg"

func save_settings() -> void:
	var cfg := ConfigFile.new()
	cfg.set_value("audio",   "master",     master_volume)
	cfg.set_value("audio",   "sfx",        sfx_volume)
	cfg.set_value("audio",   "music",      music_volume)
	cfg.set_value("display", "brightness", brightness)
	cfg.set_value("display", "fullscreen", fullscreen)
	cfg.set_value("game",    "language",   language)
	cfg.save(SETTINGS_PATH)

func load_settings() -> void:
	var cfg := ConfigFile.new()
	if cfg.load(SETTINGS_PATH) != OK:
		return
	master_volume = cfg.get_value("audio",   "master",     0.8)
	sfx_volume    = cfg.get_value("audio",   "sfx",        0.8)
	music_volume  = cfg.get_value("audio",   "music",      0.6)
	brightness    = cfg.get_value("display", "brightness", 0.7)
	fullscreen    = cfg.get_value("display", "fullscreen", false)
	language      = cfg.get_value("game",    "language",   "pt_BR")

func clear_save() -> void:
	var dir := DirAccess.open("user://")
	if dir != null and dir.file_exists("settings.cfg"):
		dir.remove("settings.cfg")

# ── Navegacao de cenas ────────────────────────────────────────
func change_scene(path: String) -> void:
	get_tree().change_scene_to_file(path)
