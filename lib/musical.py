# coding=utf-8
import re

KEY = re.compile('[A-G][b#]?m?')
CHORD = re.compile('([A-G][b#]?)')

_CHORDS_SHARP = ['A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#']
_CHORDS_FLAT =  ['A', 'Bb', 'B', 'C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab']

def transpose(chord, transposition):
    """
    Транспозиция аккорда

    :type chord: unicode
    :type transposition: int
    :rtype: unicode
    """
    if not transposition:
        return chord

    chords = _CHORDS_FLAT if chord.endswith('b') or transposition < 0 else _CHORDS_SHARP
    return chords[(chords.index(chord) + 12 + transposition) % 12]


def pretty_chord(chord, transposition, unicodeAdjustments=False):
    """
    Форматирование аккорда

    :type chord: str or unicode
    :type transposition: int
    :rtype: unicode
    """
    chord = unicode(chord)
    chord = CHORD.sub(lambda m: transpose(m.group(1), transposition), chord)
    if unicodeAdjustments:
        chord = chord.replace('b', u'\u266D')
        chord = chord.replace('#', u'\u266F')
    return chord
