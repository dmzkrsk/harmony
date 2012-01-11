# coding=utf-8
from itertools import groupby, imap
from operator import itemgetter
import os
from lib.color import RandomColorGenerator
from lib.musical.type import Length
from song import validator
from song.structure import BaseStructure
import settings

from PIL import Image, ImageDraw, ImageFont

class Chord(object):
    def __init__(self, rawChord, color):
        """
        :type rawChord: RawChord
        :type color: str or RandomColor
        """

        self.name = rawChord.name
        self.length = rawChord.length
        self.color = color

class Progression(object):
    def __init__(self, title, repeats, chords):
        """
        Отображение элемента progressions/progression для графической схемы

        :type title: unicode
        :type repeats: int
        :type chords: list(RawChord)
        """
        self.title = title
        self.repeats = repeats
        self.chords = chords

    def length(self):
        """
        :return: Длина прогрессии
        :rtype: Length
        """
        return sum(x.length for x in self.chords)

class Section(object):
    def __init__(self, title, repeats, progressions):
        """
        :type title: unicode
        :type repeats: int
        :type progressions: list(Progression)
        """
        self.title = title
        self.repeats = repeats
        self.progressions = progressions

class Structure(BaseStructure):
    """
    Класс для графической презентации структуры песни
    """

    def __init__(self, declaredLength, bpm, transposition, structure, sections, progressions):
        """
        :type declaredLength: float
        :type bpm: float
        :type transposition: int
        :type structure: xml.dom.minidom.Element
        :type sections: dict
        :type progressions: dict
        """

        self._structure = []
        self._colorGenerator = RandomColorGenerator()

        super(Structure, self).__init__(declaredLength, bpm, transposition, structure, sections, progressions)

    def finishStructure(self):
        """
        Окончание обработки структуры

        Генерируем цвета
        """
        self._colorGenerator.generateColors()

    def processSection(self, section, spIter):
        """
        Обработка содержимого секции

        :type section: xml.dom.minidom.Element
        :type spIter: SectionProgressionsIterator
        :rtype: None
        """
        title = section.getAttribute('title')

        progressions = []
        for progression, repeats in imap(itemgetter(0), groupby(imap(lambda x: (x[0], x[2]), spIter))):
            chords = [Chord(x, self._colorGenerator[(progression.title, x.name)]) for x in progression.rawChords]
            progressions.append(Progression(progression.title, repeats, chords))
        repeats = validator.repeats(section.getAttribute('repeat'))
        self._structure.append(Section(title, repeats, progressions))

    def drawStructure(self, W, H, wEff):
        """
        Генерация изображения со структурой

        :type H: int
        :type W: int
        :type wEff: int
        """

        lines = sum(x.repeats * len(x.progressions) for x in self._structure)
        extraH = settings.STRUCTURE_LINE_SPACE * (lines + len(self._structure) - 1)\
            + settings.STRUCTURE_GROUP_SPACE * (len(self._structure) - 1)
        lineH = (H - extraH) // (lines + len(self._structure))

        maxBarSize = max(
            progression.length()
            for section in self._structure
            for progression in section.progressions
        )

        im = Image.new('RGBA', (W, H))
        draw = ImageDraw.Draw(im)
        font = ImageFont.truetype(os.path.join('res', 'DejaVuSans.ttf'), int(lineH * .9))
        draw.setfont(font)

        yPos = 0

        for section in self._structure:
            title = section.title
            if section.repeats > 1:
                title += ' x%d' % section.repeats
            draw.text((4, yPos), title)
            yPos += lineH + settings.STRUCTURE_LINE_SPACE

            for progression in section.progressions:
                xPos = 0
                pos = Length(0, 1)
                for chord in progression.chords:
                    pos += chord.length
                    barX = 2 * pos.count(maxBarSize) * wEff // 3
                    draw.rectangle([(xPos, yPos), (barX, yPos + lineH)],
                        outline='black',
                        fill=str(chord.color))

                    xPos = barX

                xPos = 2 * wEff // 3
                title = [x for x in [progression.title, 'x%d' % progression.repeats if progression.repeats > 1 else ''] if x]
                draw.text((xPos + 4, int(round(yPos + lineH * .05))), ' '.join(title))

                yPos += settings.STRUCTURE_LINE_SPACE + lineH

            yPos += settings.STRUCTURE_GROUP_SPACE

        del draw
        return im
