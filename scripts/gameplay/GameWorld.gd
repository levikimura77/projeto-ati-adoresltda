## GameWorld.gd
## Orquestra a gameplay: dialogo inicial, combate, vitoria/derrota.
extends Node2D

# ── Referencias da cena ───────────────────────────────────────
@onready var player: CharacterBody2D    = $Player
@onready var boss: CharacterBody2D      = $Boss
@onready var npc: Node2D                = $NPCGuide

# HUD
@onready var player_hp_bar: ProgressBar = $HUD/PlayerHP
@onready var boss_hp_bar: ProgressBar   = $HUD/BossHP
@onready var boss_hp_label: Label       = $HUD/BossHPLabel
@onready var controls_hint: Label       = $HUD/ControlsHint

# Dialogo
@onready var dialogue_box: PanelContainer = $HUD/DialogueBox
@onready var speaker_label: Label         = $HUD/DialogueBox/VBox/SpeakerLabel
@onready var dialogue_text: Label         = $HUD/DialogueBox/VBox/DialogueText

# ── Estado ────────────────────────────────────────────────────
enum Phase { INTRO, COMBAT, WON, LOST }
var _phase: Phase = Phase.INTRO
var _step: int    = 0

# Dialogos do NPC guia
var _dialogues: Array[Dictionary] = [
	{
		"speaker": "Lider (Aticadores)",
		"text": "Ei, {name}! Que bom ter voce na equipe!\nSomos os Aticadores LTDA — o melhor grupo da escola!"
	},
	{
		"speaker": "Lider (Aticadores)",
		"text": "Existe uma hierarquia oculta aqui. A Sala Branca controla tudo\ne impede que a resenha se espalhe pela escola."
	},
	{
		"speaker": "Lider (Aticadores)",
		"text": "CONTROLES DO JOGO:\n  W / A / S / D  ou  Setas  —  Mover\n  ESPACO ou Z              —  Dar soco"
	},
	{
		"speaker": "Lider (Aticadores)",
		"text": "Olha ali! O CHEFAO da Sala Vermelha esta nos desafiando!\nEle e forte, mas voce consegue derrota-lo com seus socos. Vai la!"
	},
]

func _ready() -> void:
	player_hp_bar.max_value = player.hp_max
	player_hp_bar.value     = player.hp
	boss_hp_bar.max_value   = boss.hp_max
	boss_hp_bar.value       = boss.hp

	dialogue_box.visible  = false
	controls_hint.visible = false

	player.player_died.connect(_on_player_died)
	player.punch_landed.connect(_on_punch_landed)
	boss.boss_died.connect(_on_boss_died)
	boss.set_target(player)

	await get_tree().create_timer(0.4).timeout
	_show_dialogue()

func _unhandled_input(event: InputEvent) -> void:
	if _phase == Phase.INTRO:
		if Input.is_action_just_pressed("dialogue_next"):
			_step += 1
			_show_dialogue()

func _show_dialogue() -> void:
	if _step >= _dialogues.size():
		_end_dialogue()
		return
	var d: Dictionary = _dialogues[_step]
	speaker_label.text   = str(d["speaker"]) + ":"
	dialogue_text.text   = str(d["text"]).replace("{name}", GameState.player_name)
	dialogue_box.visible = true

func _end_dialogue() -> void:
	dialogue_box.visible  = false
	controls_hint.visible = true
	controls_hint.text    = "WASD / Setas: Mover  |  ESPACO / Z: Soco  —  Derrote o Chefao!"
	_phase = Phase.COMBAT
	player.enable_combat()
	boss.activate()

# ── Sinais de combate ─────────────────────────────────────────
func _on_punch_landed(area: Area2D) -> void:
	if _phase != Phase.COMBAT:
		return
	if not is_instance_valid(boss):
		return
	var boss_hit: Node = boss.get_node_or_null("HitArea")
	if boss_hit != null and (area == boss_hit or area.get_parent() == boss):
		boss.take_damage(20)
		boss_hp_bar.value = boss.hp

func _on_boss_died() -> void:
	if _phase == Phase.WON:
		return
	_phase = Phase.WON
	controls_hint.text = "Voce derrotou o Chefao!"
	await get_tree().create_timer(1.5).timeout
	GameState.change_scene("res://scenes/ui/BetaComplete.tscn")

func _on_player_died() -> void:
	if _phase == Phase.LOST:
		return
	_phase = Phase.LOST
	boss.active = false
	controls_hint.text   = "Voce foi derrotado... Tentando novamente..."
	speaker_label.text   = "Lider:"
	dialogue_text.text   = "Nao desista! Voce consegue!"
	dialogue_box.visible = true
	await get_tree().create_timer(2.5).timeout
	GameState.change_scene("res://scenes/gameplay/GameWorld.tscn")

func _process(_delta: float) -> void:
	if is_instance_valid(player):
		player_hp_bar.value = player.hp
	if is_instance_valid(boss):
		boss_hp_bar.value  = boss.hp
		boss_hp_label.text = "Chefao  %d / %d" % [boss.hp, boss.hp_max]
