# coding=utf-8
from . import CHORD
from transpose import transpose

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
