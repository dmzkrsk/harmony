# coding=utf-8
import re

KEY = re.compile('[A-G][b#]?m?')
CHORD = re.compile('([A-G][b#]?)')

_CIRCLE_OF_FIFTH = ['Gb', 'Db', 'Ab', 'Eb', 'Bb', 'F', 'C', 'G', 'D', 'A', 'E', 'B', 'F#', 'C#', 'G#', 'D#', 'A#']
_NOTES = 'ABCDEFG'

_CHORDS_SHARP = ['A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#']
_CHORDS_FLAT =  ['A', 'Bb', 'B', 'C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab']

_CHORD_SPECIAL = {'B#': 3, 'Cb': 2, 'E#': 8, 'Fb': 7}

def value(note):
    """
    Возвращает значение ноты

    :type note: unicode or str
    :rtype: int
    """

    if note in _CHORD_SPECIAL:
        return _CHORD_SPECIAL[note]

    if note.endswith('b'):
        return _CHORDS_FLAT.index(note)

    return _CHORDS_SHARP.index(note)
