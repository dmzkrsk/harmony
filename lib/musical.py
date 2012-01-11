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

def transpose(note, key, transposition):
    """
    Транспозиция аккорда с учетом тональности

    :type note: unicode
    :type key: unicode
    :type transposition: unicode
    :rtype: unicode
    """
    if transposition is None:
        return note

    if key.endswith('m') != transposition.endswith('m'):
        raise ValueError(u"Транспозиция из %s в %s не поддерживается" % (key, transposition))

    noteDelta = _NOTES.index(transposition[0]) - _NOTES.index(key[0])
    valueDelta = value(transposition[:-1]) -value(key[:-1])

    newValue = value(note) + valueDelta
    newNote = _NOTES[(_NOTES.index(note[0]) + noteDelta + len(_NOTES)) % len(_NOTES)]
    newNoteValue = value(newNote)

    delta = newValue - newNoteValue
    if delta > 6:
        delta -= 12
    elif delta < -6:
        delta += 12

    if not delta:
        return newNote
    elif delta < 0:
        return newNote + 'b' * -delta
    else:
        return newNote + '#' * delta


def pretty_chord(chord, key, transposition, unicodeAdjustments=False):
    """
    Форматирование аккорда

    :type chord: str or unicode
    :type key: unicode
    :type transposition: unicode
    :rtype: unicode
    """
    chord = unicode(chord)
    chord = CHORD.sub(lambda m: transpose(m.group(1), key, transposition), chord)
    if unicodeAdjustments:
        chord = chord.replace('b', u'\u266D')
        chord = chord.replace('#', u'\u266F')
    return chord
