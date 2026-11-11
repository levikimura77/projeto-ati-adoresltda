## CharacterSelect.gd
## Tela de selecao de personagem: nome + Menino / Menina.
extends Control

@onready var name_input: LineEdit     = $Panel/VBox/NameRow/NameInput
@onready var char_display: ColorRect  = $Panel/VBox/CharRow/CharPanel/CharDisplay
@onready var char_label: Label        = $Panel/VBox/CharRow/CharPanel/CharLabel
@onready var char_icon: Label         = $Panel/VBox/CharRow/CharPanel/CharIcon
@onready var left_arrow: Button       = $Panel/VBox/CharRow/LeftArrow
@onready var right_arrow: Button      = $Panel/VBox/CharRow/RightArrow
@onready var ok_btn: Button           = $Panel/VBox/OKButton
@onready var back_btn: Button         = $BackButton
@onready var error_label: Label       = $Panel/VBox/ErrorLabel

const CHARS: Array[Dictionary] = [
	{"gender": "boy",  "label": "", "color": Color(0.25, 0.45, 0.85), "icon": "Masculino"},
	{"gender": "girl", "label": "", "color": Color(0.75, 0.35, 0.70), "icon": "Feminino"},
]
var _index: int = 0

func _ready() -> void:
	error_label.visible = false
	left_arrow.pressed.connect(_prev)
	right_arrow.pressed.connect(_next)
	ok_btn.pressed.connect(_on_ok)
	back_btn.pressed.connect(_on_back)
	if GameState.player_name != "Jogador":
		name_input.text = GameState.player_name
	_refresh()

func _prev() -> void:
	_index = (_index - 1 + CHARS.size()) % CHARS.size()
	_refresh()

func _next() -> void:
	_index = (_index + 1) % CHARS.size()
	_refresh()

func _refresh() -> void:
	var ch: Dictionary = CHARS[_index]
	char_display.color = ch["color"]
	char_label.text    = ch["label"]
	char_icon.text     = ch["icon"]

func _on_ok() -> void:
	var pname: String = name_input.text.strip_edges()
	if pname.is_empty():
		error_label.visible = true
		error_label.text    = "Por favor, digite seu nome!"
		return
	error_label.visible     = false
	GameState.player_name   = pname
	GameState.player_gender = CHARS[_index]["gender"]
	GameState.change_scene("res://scenes/gameplay/GameWorld.tscn")

func _on_back() -> void:
	GameState.change_scene("res://scenes/ui/MainMenu.tscn")
