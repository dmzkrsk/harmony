# -*- coding: utf-8 -*-
"""
Разбор последовательностей и секций
"""
import abc
from . import ParseException, iterElements
from type.structure import *
import validator

class Loader(object):
    """
    Базовый класс парсеров структур progression и section
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, node, stag):
        """
        :type node: xml.dom.minidom.Element
        :type stag: str
        """
        self.values = {}

        for element in iterElements(node):
            if element.tagName != stag:
                raise ParseException(u"Элемент %s не может содержать элемент %s" % (node.tagName, element.tagName))

            self.processElement(element)

    @abc.abstractmethod
    def processElement(self, element):
        """
        Специфичная для класса обработка элемента

        :type element: xml.dom.minidom.Element
        :rtype: None
        """
        pass

    @staticmethod
    def id(f):
        """
        Декораток, который проверяет наличие уникального аттрибута ID

        :type f: function
        :rtype: function
        """
        def _wrapper(self, element):
            """
            :type element: xml.dom.minidom.Element
            :rtype: None
            """
            if not element.hasAttribute('id'):
                raise ParseException(u"Элемент %s должен содержать аттрибут ID" % element.tagName)

            id = element.getAttribute('id')
            if id in self.values:
                raise ParseException(u'Элемент %s#%s уже определен' % (element.tagName, id))

            return f(self, element)
        return _wrapper

class SectionLoader(Loader):
    """
    Обработчик sections/section
    """
    def __init__(self, node):
        """
        :type node: xml.dom.minidom.Element
        """
        super(SectionLoader, self).__init__(node, 'section')

    @Loader.id
    def processElement(self, element):
        """
        Специфичная для класса обработка элемента

        Конструрием элементы из аттрибутов элемента

        :type element: xml.dom.minidom.Element
        :rtype: None
        """
        id = element.getAttribute('id')

        progressions = [
            SectionProgression(
                x.getAttribute('ref'),
                validator.repeats(x.getAttribute('repeat'))
            )
            for x in iterElements(element)
        ]

        if not progressions:
            raise ParseException(u"Секция %s пуста" % id)

        self.values[id] = Section(progressions)

class ProgressionLoader(Loader):
    """
    обработчик progressions/progression
    """
    def __init__(self, node):
        super(ProgressionLoader, self).__init__(node, 'progression')

    @Loader.id
    def processElement(self, element):
        """
        Специфичная для класса обработка элемента

        Конструрием элементы из аттрибутов элемента

        :type element: xml.dom.minidom.Element
        :rtype: None
        """
        id = element.getAttribute('id')
        signature = validator.signature(element.getAttribute('signature'))
        title = element.getAttribute('title')

        chords = [self.processStructure(x, signature[0]) for x in iterElements(element)]

        if not chords:
            raise ParseException(u"Последовательность %s пуста" % id)

        self.validate(id, chords, signature[0])

        self.values[id] = Progression(signature, title, chords)

    @classmethod
    def validate(cls, id, chords, beats):
        """
        Проверяем, что такт заполнен полностью

        :type id: str or unicode
        :type chords: list(RawChord)
        :type beats: int
        :rtype: None
        """
        beatsCurrent = sum(x.beats for x in chords)

        if beatsCurrent % beats:
            beatsUp = beatsCurrent + beats - beatsCurrent % beats
            raise ParseException(u'Незаконченный такт в последовательности %s: %d of %d' % (id, beats, beatsUp))

    @classmethod
    def processStructure(cls, structureElement, beats):
        """
        Генерация элементов RawChord

        Необходимо расчитать размер в долях

        :type structureElement: xml.dom.minidom.Element
        :type beats: int
        :rtype: None
        """
        repeats = validator.repeats(structureElement.getAttribute('repeat'))
        chord = structureElement.getAttribute('chord')
        if structureElement.tagName in ['empty-bar', 'bar']:
            return RawChord(chord, beats * repeats)
        elif structureElement.tagName in ['empty-beat', 'beat']:
            return RawChord(chord, repeats)
        else:
            raise ParseException(u"Элемент %s не может содержать элемент %s" % (structureElement.parentNode.tagName, structureElement.tagName))
