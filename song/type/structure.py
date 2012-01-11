# coding=utf-8
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

    def seconds(self, bpm):
        """
        Длина в секундах

        :type bpm: float
        :rtype: float
        """

        return self.length.seconds(bpm)

class Progression(object):
    """
    Отображение элемента progressions/progression
    """
    def __init__(self, signature, title, rawChords):
        """
        :type signature: Length
        :type title: str or unicode
        :type rawChords: list(RawChord)
        """
        self.signature = signature
        self.title = title
        self.rawChords = rawChords

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
