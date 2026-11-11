## Boss.gd
## Chefao: persegue o jogador e ataca em intervalos.
extends CharacterBody2D

signal boss_died

const SPEED: float           = 65.0
const ATTACK_INTERVAL: float = 1.8
const ATTACK_RANGE: float    = 72.0
const DAMAGE: int            = 10

var hp: int      = 200
var hp_max: int  = 200
var active: bool = false

var _attack_timer: float = 0.0
var _target: Node2D      = null

@onready var body_rect: ColorRect = $Body

func set_target(t: Node2D) -> void:
	_target = t

func activate() -> void:
	active = true

func _physics_process(delta: float) -> void:
	if not active or _target == null or hp <= 0:
		return

	var dir: Vector2 = (_target.global_position - global_position).normalized()
	velocity = dir * SPEED
	move_and_slide()

	_attack_timer += delta
	if _attack_timer >= ATTACK_INTERVAL:
		_attack_timer = 0.0
		if global_position.distance_to(_target.global_position) <= ATTACK_RANGE:
			_do_attack()

func _do_attack() -> void:
	if _target == null or hp <= 0:
		return
	if _target.has_method("take_damage"):
		_target.take_damage(DAMAGE)
	_flash_attack()

func take_damage(amount: int) -> void:
	if hp <= 0:
		return
	hp = max(hp - amount, 0)
	_flash_hit()
	if hp <= 0:
		boss_died.emit()
		_die()

func _die() -> void:
	active = false
	velocity = Vector2.ZERO
	var tween := create_tween()
	tween.tween_property(self, "modulate:a", 0.0, 0.6)
	await tween.finished
	queue_free()

func _flash_hit() -> void:
	if not is_instance_valid(body_rect):
		return
	body_rect.color = Color.WHITE
	await get_tree().create_timer(0.12).timeout
	if is_instance_valid(self) and is_instance_valid(body_rect) and hp > 0:
		body_rect.color = Color(0.65, 0.08, 0.08)

func _flash_attack() -> void:
	if not is_instance_valid(body_rect):
		return
	body_rect.color = Color(1.0, 0.6, 0.05)
	await get_tree().create_timer(0.15).timeout
	if is_instance_valid(self) and is_instance_valid(body_rect) and hp > 0:
		body_rect.color = Color(0.65, 0.08, 0.08)
