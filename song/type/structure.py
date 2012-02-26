# coding=utf-8
from lib.color import RandomColorGenerator

class RawChord(object):
    """
    Отображение элемента progression/chord
    """
    def __init__(self, name, length):
        """
        :type name: str or unicode
        :type length: Length
        """
        self.name = name
        self.length = length

class Progression(object):
    """
    Отображение элемента progressions/progression
    """
    def __init__(self, signature, title, rawChords, key):
        """
        :type signature: Length
        :type title: str or unicode
        :type rawChords: list(RawChord)
        """
        self.signature = signature
        self.title = title
        self.rawChords = rawChords
        self.key = key
        self._colorGenerator = RandomColorGenerator()

    def color(self, chord):
        return self._colorGenerator[(chord,)]

    def beatCount(self):
        """
        Количество долей в последовательности
        """
        length = sum(x.length for x in self.rawChords)
        return length.numerator * self.signature.denominator / length.denominator

class SectionProgression(object):
    """
    Отображение элемента section/progression

    Хранит текстовую "ссылку" на Progression кол-во повтором
    """
    def __init__(self, progressionRef, repeats):
        """
        :type progressionRef: str
        :type repeats: int
        """
        self.progressionRef = progressionRef
        self.repeats = repeats

class Section(object):
    """
    Отображение элемента sections/section
    """
    def __init__(self, progressions):
        """
        :type progressions: list(SectionProgression)
        """
        self.progressions = progressions
