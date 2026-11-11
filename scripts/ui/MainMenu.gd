## MainMenu.gd
## Menu principal com botoes: Jogar, Opcoes, Creditos, Sair.
extends Control

@onready var play_btn: TextureButton           = $PlayButton
@onready var options_btn: TextureButton        = $OptionsButton
@onready var credits_btn: TextureButton        = $CreditsButton
@onready var quit_btn: TextureButton           = $QuitButton
@onready var credits_popup: AcceptDialog = $CreditsPopup
@onready var version_label: Label       = $VersionLabel

func _ready() -> void:
	version_label.text = "Versao Beta"
	play_btn.pressed.connect(_on_play)
	options_btn.pressed.connect(_on_options)
	credits_btn.pressed.connect(_on_credits)
	quit_btn.pressed.connect(_on_quit)

	for btn: TextureButton in [play_btn, options_btn, credits_btn, quit_btn]:
		btn.mouse_entered.connect(func(): btn.modulate = Color(1.15, 1.15, 1.15))
		btn.mouse_exited.connect(func(): btn.modulate = Color.WHITE)

func _on_play() -> void:
	GameState.change_scene("res://scenes/ui/CharacterSelect.tscn")

func _on_options() -> void:
	GameState.change_scene("res://scenes/ui/SettingsScreen.tscn")

func _on_credits() -> void:
	credits_popup.popup_centered()

func _on_quit() -> void:
	get_tree().quit()
