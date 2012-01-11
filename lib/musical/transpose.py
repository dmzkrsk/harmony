# coding=utf-8
from . import _NOTES, value

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
