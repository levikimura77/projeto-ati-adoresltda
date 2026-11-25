"""Temas calmos para a campanha e voz no estilo dos jogos de 8 bits."""

import math
from array import array
from functools import lru_cache


RATE = 22050
# BPM, acordes por compasso e melodia por batida. None deixa espaço entre as frases.
THEMES = (
    (60, ((48, 4), (45, 3), (41, 4), (43, 4)),
     (64, None, 67, 72, 69, None, 64, None, 65, None, 69, 72, 71, None, 67, None)),
    (58, ((48, 4), (40, 3), (41, 4), (43, 4)),
     (67, None, 64, None, 71, None, 67, 64, 65, None, 69, None, 67, 69, 62, None)),
    (60, ((50, 3), (47, 3), (43, 4), (45, 4)),
     (65, None, 69, None, 66, 71, None, 74, 71, None, 67, None, 69, None, 64, None)),
    (55, ((45, 3), (41, 4), (48, 4), (43, 4)),
     (64, None, 69, None, 65, None, 72, None, 67, None, 76, 72, 71, None, 67, None)),
)


@lru_cache(maxsize=256)
def note_wave(note, beat, length, voice):
    count = int(beat*length)
    step = 440.0*2**((note-69)/12)/RATE
    wave = array("h")
    for i in range(count):
        phase = (i*step) % 1
        triangle = 1 - 4*abs(phase-.5)
        if voice == "speech":
            signal = .78*triangle + .22*(1 if phase < .35 else -1)
            envelope = min(1, i/245, (count-i)/max(1, count*.35))
            amplitude = 3000
        else:
            fundamental = math.sin(math.tau*phase)
            harmonic = math.sin(2*math.tau*phase)
            if voice == "keys":
                signal = .84*fundamental + .16*harmonic
                envelope = min(1, i/(RATE*.045), (count-i)/max(1, count*.55))
                amplitude = 2300
            else:
                signal = .92*fundamental + .08*triangle
                envelope = min(1, i/(RATE*.2), (count-i)/max(1, count*.42))
                amplitude = 820
        wave.append(round(signal*envelope*amplitude))
    return wave


def theme_pcm(index):
    bpm, chords, melody = THEMES[index]
    beat = round(60*RATE/bpm)
    mix = array("h", [0])*(beat*len(melody))

    def add(note, when, length, voice):
        for i, value in enumerate(note_wave(note, beat, length, voice)):
            mix[when+i] += value

    for bar, (root, third) in enumerate(chords):
        start = bar*4*beat
        add(root, start, 3.75, "pad")
        add(root+third+12, start+beat//2, 3.2, "pad")
        add(root+7, start+beat, 2.75, "pad")
    for tick, note in enumerate(melody):
        if note is not None:
            add(note, tick*beat, 1.6 if tick < 15 and melody[tick+1] is None else .89, "keys")
    stereo = array("h", [0])*(len(mix)*2)
    stereo[::2] = stereo[1::2] = mix
    return stereo.tobytes()


def speech_pcm(text, speaker):
    """Sons curtos espaçados por palavras e pontuação, com altura por personagem."""
    base = 57 + sum(map(ord, speaker)) % 15
    tick = round(RATE*.035)
    mix = array("h")
    for index, letter in enumerate(text):
        if letter in ",.!?;":
            mix.extend([0]*(tick*4))
        elif letter.isspace() or index % 2:
            mix.extend([0]*tick)
        elif letter.isalpha():
            mix.extend(note_wave(base+(ord(letter.lower()) % 6), tick, 1, "speech"))
    stereo = array("h", [0])*(len(mix)*2)
    stereo[::2] = stereo[1::2] = mix
    return stereo.tobytes()
