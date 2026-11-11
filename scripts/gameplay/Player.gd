## Player.gd
## Controla o personagem do jogador: movimento top-down e socos.
extends CharacterBody2D

signal player_died
signal punch_landed(area: Area2D)

const SPEED: float             = 200.0
const PUNCH_COOLDOWN: float    = 0.5
const PUNCH_ACTIVE_TIME: float = 0.15

var hp: int          = 100
var hp_max: int      = 100
var can_punch: bool  = false
var _punch_cd: float = 0.0
var _punching: bool  = false
var _base_color: Color = Color(0.25, 0.45, 0.85)

@onready var body_rect: ColorRect         = $Body
@onready var head_rect: ColorRect         = $Head
@onready var name_label: Label            = $NameLabel
@onready var punch_area: Area2D           = $PunchArea
@onready var punch_shape: CollisionShape2D = $PunchArea/PunchShape
@onready var punch_flash: ColorRect       = $PunchFlash

func _ready() -> void:
	name_label.text = GameState.player_name
	if GameState.player_gender == "boy":
		_base_color = Color(0.25, 0.45, 0.85)
	else:
		_base_color = Color(0.75, 0.35, 0.70)
	body_rect.color      = _base_color
	punch_shape.disabled = true
	punch_flash.visible  = false

func _physics_process(delta: float) -> void:
	_punch_cd = maxf(_punch_cd - delta, 0.0)

	var dir := Vector2.ZERO
	if Input.is_action_pressed("move_right"): dir.x += 1.0
	if Input.is_action_pressed("move_left"):  dir.x -= 1.0
	if Input.is_action_pressed("move_down"):  dir.y += 1.0
	if Input.is_action_pressed("move_up"):    dir.y -= 1.0
	velocity = dir.normalized() * SPEED
	move_and_slide()

	if can_punch and not _punching and _punch_cd <= 0.0:
		if Input.is_action_just_pressed("punch"):
			_do_punch()

func _do_punch() -> void:
	_punching = true
	_punch_cd = PUNCH_COOLDOWN
	punch_flash.visible  = true
	punch_shape.disabled = false

	# Force physics to update overlaps before checking
	await get_tree().physics_frame
	for area: Area2D in punch_area.get_overlapping_areas():
		punch_landed.emit(area)

	await get_tree().create_timer(PUNCH_ACTIVE_TIME).timeout
	if is_instance_valid(self):
		punch_shape.disabled = true
		punch_flash.visible  = false
		_punching = false

func take_damage(amount: int) -> void:
	if hp <= 0:
		return
	hp = max(hp - amount, 0)
	_flash(Color(1.0, 0.2, 0.2))
	if hp <= 0:
		player_died.emit()

func enable_combat() -> void:
	can_punch = true

func _flash(color: Color) -> void:
	body_rect.color = color
	await get_tree().create_timer(0.2).timeout
	if is_instance_valid(self):
		body_rect.color = _base_color
