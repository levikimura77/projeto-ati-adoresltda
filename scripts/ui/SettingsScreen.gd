## SettingsScreen.gd
## Tela de configuracoes: tela, audio, musica, idioma, dados salvos.
extends Control

@onready var fullscreen_check: CheckBox   = $MainPanel/HBox/ContentVBox/FullscreenCheck
@onready var brightness_slider: HSlider  = $MainPanel/HBox/ContentVBox/BrightnessRow/BrightnessSlider
@onready var brightness_val: Label       = $MainPanel/HBox/ContentVBox/BrightnessRow/BrightnessValue
@onready var master_slider: HSlider      = $MainPanel/HBox/ContentVBox/MasterRow/MasterSlider
@onready var master_val: Label           = $MainPanel/HBox/ContentVBox/MasterRow/MasterValue
@onready var sfx_slider: HSlider         = $MainPanel/HBox/ContentVBox/SFXRow/SFXSlider
@onready var sfx_val: Label              = $MainPanel/HBox/ContentVBox/SFXRow/SFXValue
@onready var music_slider: HSlider       = $MainPanel/HBox/ContentVBox/MusicRow/MusicSlider
@onready var music_val: Label            = $MainPanel/HBox/ContentVBox/MusicRow/MusicValue
@onready var language_option: OptionButton = $MainPanel/HBox/ContentVBox/LanguageOption
@onready var clear_save_btn: Button      = $MainPanel/HBox/ContentVBox/ClearSaveButton
@onready var cancel_btn: Button          = $MainPanel/HBox/ContentVBox/ButtonRow/CancelButton
@onready var save_btn: Button            = $MainPanel/HBox/ContentVBox/ButtonRow/SaveButton
@onready var feedback_label: Label       = $MainPanel/HBox/ContentVBox/FeedbackLabel

func _ready() -> void:
	language_option.add_item("Portugues (Brasil)", 0)
	language_option.add_item("English", 1)

	fullscreen_check.button_pressed = GameState.fullscreen
	brightness_slider.value = GameState.brightness
	master_slider.value     = GameState.master_volume
	sfx_slider.value        = GameState.sfx_volume
	music_slider.value      = GameState.music_volume
	language_option.selected = 0 if GameState.language == "pt_BR" else 1

	_update_labels()

	brightness_slider.value_changed.connect(func(_v: float): _update_labels())
	master_slider.value_changed.connect(func(_v: float): _update_labels())
	sfx_slider.value_changed.connect(func(_v: float): _update_labels())
	music_slider.value_changed.connect(func(_v: float): _update_labels())

	save_btn.pressed.connect(_on_save)
	cancel_btn.pressed.connect(_on_cancel)
	clear_save_btn.pressed.connect(_on_clear_save)

	feedback_label.visible = false

func _update_labels() -> void:
	brightness_val.text = "%d" % int(brightness_slider.value * 100.0)
	master_val.text     = "%d" % int(master_slider.value * 100.0)
	sfx_val.text        = "%d" % int(sfx_slider.value * 100.0)
	music_val.text      = "%d" % int(music_slider.value * 100.0)

func _on_save() -> void:
	GameState.fullscreen    = fullscreen_check.button_pressed
	GameState.brightness    = brightness_slider.value
	GameState.master_volume = master_slider.value
	GameState.sfx_volume    = sfx_slider.value
	GameState.music_volume  = music_slider.value
	GameState.language      = "pt_BR" if language_option.selected == 0 else "en"

	if GameState.fullscreen:
		DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_FULLSCREEN)
	else:
		DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_WINDOWED)

	GameState.save_settings()
	feedback_label.text    = "Configuracoes salvas!"
	feedback_label.visible = true
	await get_tree().create_timer(1.0).timeout
	GameState.change_scene("res://scenes/ui/MainMenu.tscn")

func _on_cancel() -> void:
	GameState.change_scene("res://scenes/ui/MainMenu.tscn")

func _on_clear_save() -> void:
	GameState.clear_save()
	feedback_label.text    = "Dados salvos excluidos!"
	feedback_label.visible = true
