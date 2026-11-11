## LoadingScreen.gd
## Tela de carregamento animada que avanca para o menu principal.
extends Control

@onready var progress_bar: ProgressBar = $CenterBox/VBox/ProgressBar
@onready var loading_label: Label      = $CenterBox/VBox/LoadingLabel
@onready var tick_timer: Timer         = $TickTimer
@onready var dot_timer: Timer          = $DotTimer

var _progress: float = 0.0
var _dot_count: int  = 0
var _done: bool      = false

const STEPS: Array[String] = [
	"Carregando assets",
	"Inicializando mundo",
	"Preparando personagens",
	"Carregando musicas",
	"Quase pronto",
]

func _ready() -> void:
	GameState.load_settings()
	_apply_fullscreen()

	progress_bar.value = 0.0
	loading_label.text = "Carregando..."

	tick_timer.wait_time = 0.04
	dot_timer.wait_time  = 0.5
	tick_timer.start()
	dot_timer.start()

	tick_timer.timeout.connect(_on_tick)
	dot_timer.timeout.connect(_on_dot)

func _apply_fullscreen() -> void:
	if GameState.fullscreen:
		DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_FULLSCREEN)

func _on_tick() -> void:
	if _done:
		return
	_progress += randf_range(2.5, 7.0)
	_progress = minf(_progress, 100.0)
	progress_bar.value = _progress

	var idx: int = int(_progress / 20.0)
	if idx < STEPS.size():
		loading_label.text = STEPS[idx]

	if _progress >= 100.0:
		_done = true
		tick_timer.stop()
		dot_timer.stop()
		loading_label.text = "Concluido!"
		await get_tree().create_timer(0.6).timeout
		GameState.change_scene("res://scenes/ui/MainMenu.tscn")

func _on_dot() -> void:
	if _done:
		return
	_dot_count = (_dot_count + 1) % 4
	var base: String = loading_label.text.rstrip(".")
	loading_label.text = base + ".".repeat(_dot_count)
