# coding=utf-8
class RawChord(object):
    """
    Отображение элемента progression/chord
    """
    def __init__(self, name, beats):
        """
        :type name: str or unicode
        :param beats: Длительность в долях такта
        :type beats: int
        """
        self.name = name
        self.beats = beats

class Progression(object):
    """
    Отображение элемента progressions/progression
    """
    def __init__(self, signature, title, rawChords):
        """
        :type signature: tuple(int, int)
        :type title: str or unicode
        :type rawChords: list(RawChord)
        """
        self.signature = signature
        self.title = title
        self.rawChords = rawChords

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