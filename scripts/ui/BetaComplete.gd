## BetaComplete.gd
## Tela exibida ao derrotar o chefao: fim da versao beta.
extends Control

@onready var name_label: Label      = $VBox/NameLabel
@onready var play_again_btn: Button = $VBox/ButtonRow/PlayAgainButton
@onready var menu_btn: Button       = $VBox/ButtonRow/MenuButton

func _ready() -> void:
	name_label.text = "%s venceu!" % GameState.player_name
	play_again_btn.pressed.connect(_on_play_again)
	menu_btn.pressed.connect(_on_menu)

	modulate.a = 0.0
	var tween := create_tween()
	tween.tween_property(self, "modulate:a", 1.0, 1.2)

func _on_play_again() -> void:
	GameState.change_scene("res://scenes/ui/CharacterSelect.tscn")

func _on_menu() -> void:
	GameState.change_scene("res://scenes/ui/MainMenu.tscn")
