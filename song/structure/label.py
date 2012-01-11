# -*- coding: utf-8 -*-
from lib.color import RandomColorGenerator
from lib.musical.chords import pretty_chord
from .. import validator
from . import BaseTimedStructure
from ..type.label import Label, LabelSheet
import settings

class Structure(BaseTimedStructure):
    """
    Парсер структуры в виде аккордов, сегментов и последовательностей
    """
    def __init__(self, declaredLength, bpm, key, transposition, structure, sections, progressions):
        """
        :type declaredLength: float
        :type bpm: float
        :type key: unicode
        :type transposition: unicode
        :type structure: xml.dom.minidom.Element
        :type sections: dict
        :type progressions: dict
        """
        self.chords = LabelSheet()
        self.sections = LabelSheet()
        self.progressions = LabelSheet()
        self._colorGenerator = RandomColorGenerator()

        self._key = key
        self._transposition = transposition

        self._colorMap = []

        super(Structure, self).__init__(declaredLength, bpm, key, transposition, structure, sections, progressions)

    def initSection(self, section, repeat, repeats):
        """
        Обработка новой секции

        Добавляем новую метку для секции и элемент в colormap

        :type section: xml.dom.minidom.Element
        :type repeat: int
        :type repeats: int
        :rtype: None
        """
        title = section.getAttribute('title')
        color = validator.color(section.getAttribute('color'), settings.SECTION_COLOR_DEFAULT)
        sectionTitle = self.makeTitle(title, repeat, repeats)
        sectionLabel = self.labelAtCurPos(sectionTitle, color)
        self.sections.append(sectionLabel)

        # Карта цвета

        if not self._colorMap and self._position > 0:
            self._colorMap.append((0, None))

        self._colorMap.append((self._position, color))

    def initProgression(self, progression, repeat, repeats):
        """
        Обработка новой последовательности

        Добавляем новую метку для последовательности

        :type progression: Progression
        :type repeat: int
        :type repeats: int
        :rtype: None
        """
        progressionTitle = self.makeTitle(progression.title, repeat, repeats)
        progressionLabel = self.labelAtCurPos(progressionTitle, settings.PROGRESSION_COLOR)
        self.progressions.append(progressionLabel)

    def processChord(self, progression, rawChord):
        """
        Обработка аккорда

        Добавляем новую метку для аккорда

        :type progression: Progression
        :type rawChord: RawChord
        :rtype: None
        """
        color = self._colorGenerator[(progression.title, rawChord.name)]
        chordLabel = self.labelAtCurPos(pretty_chord(rawChord.name, self._key, self._transposition), color)
        self.chords.append(chordLabel)

    def labelAtCurPos(self, title, color):
        """
        Вспомогательная функция для создания метки в текущей позиции

        :type title: unicode
        :type color: str or unicode or RandomColor
        :rtype: Label
        """
        return Label(title, self._position, color)

    @classmethod
    def makeTitle(cls, title, repeat, repeats):
        """
        Создает заголовок с учетом повторов

        :type title: unicode
        :type repeat: int
        :type repeats: int
        :rtype: unicode
        """
        return u'%s (%d/%d)' % (title, repeat + 1, repeats) if repeats > 1 else title

    def getColorMap(self):
        """
        :rtype: list(tuple(float, str or RandomColor))
        """
        return self._colorMap

    def finishStructure(self):
        """
        Окончание обработки структуры

        Закрываем метки, записываем в карту цвета последнюю позицию

        :rtype: None
        """
        self.chords.close(self._position)
        self.sections.close(self._position)
        self.progressions.close(self._position)

        if self._colorMap[-1][0] < self._position:
            self._colorMap.append((self._position - 1, None))
