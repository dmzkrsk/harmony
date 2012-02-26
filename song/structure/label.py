# -*- coding: utf-8 -*-
from lib.musical.chords import pretty_chord
from .. import validator, getAttr
from . import BaseTimedStructure
from ..type.label import Label, LabelSheet
import settings

class Structure(BaseTimedStructure):
    """
    Парсер структуры в виде аккордов, сегментов и последовательностей
    """

    def __init__(self, structure, sections, progressions, declaredLength, timeMap, **extra):
        self.chords = LabelSheet()
        self.sections = LabelSheet()
        self.progressions = LabelSheet()
        self.infos = LabelSheet()

        self._key = extra['key']
        self._transposition = extra['transposition']

        self._colorMap = []

        super(Structure, self).__init__(structure, sections, progressions, declaredLength, timeMap, **extra)

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
        color = getAttr(section, 'color', False, validator.color, settings.SECTION_COLOR_DEFAULT)
        sectionTitle = self.makeTitle(title, repeat, repeats)
        sectionLabel = self.labelAtCurPos(sectionTitle, color)
        self.sections.append(sectionLabel)

        # Карта цвета

        if not self._colorMap and self._bar:
            self._colorMap.append((0, None))

        self._colorMap.append((self._timeMap(self._bar), color))

    def initProgression(self, progression, repeat, repeats, **extra):
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

        abpm = self._timeMap.bpm(self._bar)

        infoLabel = u'%d bpm | %s' % (abpm, progression.key or self._key)
        infoLabel = self.labelAtCurPos(infoLabel, settings.COMMON_COLOR)
        self.infos.append(infoLabel)

    def processChord(self, progression, rawChord):
        """
        Обработка аккорда

        Добавляем новую метку для аккорда

        :type progression: Progression
        :type rawChord: RawChord
        :rtype: None
        """
        color = progression.color(rawChord.name)
        chordLabel = self.labelAtCurPos(pretty_chord(rawChord.name, self._key, self._transposition), color)
        self.chords.append(chordLabel)

    def labelAtCurPos(self, title, color):
        """
        Вспомогательная функция для создания метки в текущей позиции

        :type title: unicode
        :type color: str or unicode or RandomColor
        :rtype: Label
        """
        return Label(title, self._timeMap(self._bar), color)

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
        pos = self._timeMap(self._bar)

        self.chords.close(pos)
        self.sections.close(pos)
        self.progressions.close(pos)
        self.infos.close(pos)

        if self._colorMap[-1][0] < pos:
            self._colorMap.append((pos - 1, None))
