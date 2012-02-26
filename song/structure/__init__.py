# -*- coding: utf-8 -*-
from abc import abstractmethod
from .. import ParseException, validator, iterElements, getAttr
from lib.musical.type import Length

class SectionProgressionsIterator(object):
    """
    Итератор по структуре песни с учетом повторов
    """
    def __init__(self, ref, sections, progressions):
        """
        :type ref: str
        :type sections: dict
        :type progressions: dict
        """
        if not ref in sections:
            raise ParseException(u"Элемент section содержит аттрибут REF %s, указывающий на несуществующий элемент" % ref)

        self._section = []
        for sp in sections[ref].progressions:
            pRef = sp.progressionRef
            if not pRef or pRef not in progressions:
                raise ParseException(u"Элемент section содержит аттрибут REF %s, указывающий на несуществующий элемент" % pRef)

            self._section.append((progressions[pRef], sp.repeats))

        self.pos = 0
        self.repeat = 0

    def __iter__(self):
        """
        :rtype: SectionProgressionsIterator
        """
        return self

    def reset(self):
        """
        :rtype: None
        """
        self.pos = 0
        self.repeat = 0

    def next(self):
        """
        :rtype: tuple(Progression, int, int)
        """
        if self.pos >= len(self._section):
            raise StopIteration()

        progression, repeats = self._section[self.pos]
        repeat = self.repeat

        self.repeat += 1
        if self.repeat == repeats:
            self.repeat = 0
            self.pos += 1

        return progression, repeat, repeats

#noinspection PyUnusedLocal
class BaseStructure(object):
    """
    Базовый класс для обхода структуры при помощи DOM
    """
    def __init__(self, structure, sections, progressions, **extra):
        """
        :type structure: xml.dom.minidom.Element
        :type sections: dict
        :type progressions: dict
        """

        self._bar = Length(0)

        for element in iterElements(structure):
            if element.tagName != 'section':
                raise ParseException(u'Элемент %s не может содержать элемент %s' % (structure.tagName, element.tagName))

            if not element.hasAttribute('ref'):
                raise ParseException(u"Элемент section должен содержать аттрибут REF")
            if not element.hasAttribute('title'):
                raise ParseException(u"Элемент section должен содержать аттрибут TITLE")

            ref = element.getAttribute('ref')
            self.processSection(element, SectionProgressionsIterator(ref, sections, progressions), **extra)

        self.finishStructure()

    @abstractmethod
    def processSection(self, section, spIter, **extra):
        """
        Обработка содержимого секции
        """
        pass

    @abstractmethod
    def finishStructure(self):
        """
        Окончание обработки структуры
        """
        pass

#noinspection PyUnusedLocal
class BaseTimedStructure(BaseStructure):
    def __init__(self, structure, sections, progressions, declaredLength, timeMap, **extra):
        """
        :type structure: xml.dom.minidom.Element
        :type sections: dict
        :type progressions: dict
        :type declaredLength: float
        """
        self._timeMap = timeMap
        self._declaredLength = declaredLength

        super(BaseTimedStructure, self).__init__(structure, sections, progressions, **extra)

    def processSection(self, section, spIter, **extra):
        """
        Обработка содержимого секции

        :type section: xml.dom.minidom.Element
        :type spIter: SectionProgressionsIterator
        :rtype: None
        """
        repeats = getAttr(section, 'repeat', False, validator.repeats, 1)

        for repeat in xrange(repeats):
            self.initSection(section, repeat, repeats)

            for progression, progressionRepeat, progressionRepeats in spIter:
                self.initProgression(progression, progressionRepeat, progressionRepeats)

                for rawChord in progression.rawChords:
                    self.processChord(progression, rawChord)
                    self._bar += rawChord.length

                tpos = self._timeMap(self._bar)
                if tpos > self._declaredLength:
                    ref = section.getAttribute('ref')
                    raise ParseException(u'Позиция за пределом песни %f > %f после %s:%d/%s' % (tpos, self._declaredLength, ref, repeat + 1, progression.title))

            spIter.reset()

    @abstractmethod
    def initSection(self, section, repeat, repeats):
        """
        Обработка новой секции

        :type section: xml.dom.minidom.Element
        :type repeat: int
        :type repeats: int
        :rtype: None
        """
        pass

    @abstractmethod
    def initProgression(self, progression, repeat, repeats):
        """
        Обработка новой последовательности

        :type progression: Progression
        :type repeat: int
        :type repeats: int
        :rtype: None
        """
        pass

    @abstractmethod
    def processChord(self, progression, rawChord):
        """
        Обработка аккорда

        :type progression: Progression
        :type rawChord: RawChord
        :rtype: None
        """
        pass
