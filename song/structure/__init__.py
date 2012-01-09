# -*- coding: utf-8 -*-
from abc import abstractmethod
from .. import ParseException, validator, iterElements

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

        self.repeat += 1
        if self.repeat == repeats:
            self.repeat = 0
            self.pos += 1

        return progression, self.repeat, repeats

#noinspection PyUnusedLocal
class BaseStructure(object):
    """
    Базовый класс для обхода структуры при помощи DOM
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
        for element in iterElements(structure):
            if element.tagName != 'section':
                raise ParseException(u'Элемент %s не может содержать элемент %s' % (structure.tagName, element.tagName))

            if not element.hasAttribute('ref'):
                raise ParseException(u"Элемент section должен содержать аттрибут REF")
            if not element.hasAttribute('title'):
                raise ParseException(u"Элемент section должен содержать аттрибут TITLE")

            ref = element.getAttribute('ref')
            self.processSection(element, SectionProgressionsIterator(ref, sections, progressions))

        self.finishStructure()

    @abstractmethod
    def processSection(self, section, spIter):
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
    def __init__(self, declaredLength, bpm, transposition, structure, sections, progressions):
        self._position = validator.start(structure.getAttribute('start') or 0)
        self.declaredLength = declaredLength
        self._beatSize = 60.0 / bpm

        super(BaseTimedStructure, self).__init__(declaredLength, bpm, transposition, structure, sections, progressions)

    def processSection(self, section, spIter):
        """
        Обработка содержимого секции

        :type section: xml.dom.minidom.Element
        :type spIter: SectionProgressionsIterator
        :rtype: None
        """
        repeats = validator.repeats(section.getAttribute('repeat'))

        for repeat in xrange(repeats):
            self.initSection(section, repeat, repeats)

            for progression, progressionRepeat, progressionRepeats in spIter:
                self.initProgression(progression, progressionRepeat, progressionRepeats)

                for rawChord in progression.rawChords:
                    self.processChord(progression, rawChord)
                    shift = rawChord.beats * self._beatSize
                    self._position += shift

                if self._position > self.declaredLength:
                    raise ParseException(u'Позиция за пределом песни %f > %f после %s:%d/%s' % (self._position, self.declaredLength, section.getAttribute('ref'), repeat + 1, progression.title))

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
