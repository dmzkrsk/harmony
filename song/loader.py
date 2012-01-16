# -*- coding: utf-8 -*-
"""
Разбор последовательностей и секций
"""
import abc
from . import ParseException, iterElements
from lib.musical.type import Length
from lib.musical.validator import key as validator_key
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
        signature = Length.validator(element.getAttribute('signature'))
        title = element.getAttribute('title')
        key = validator_key(element.getAttribute('key')) if element.hasAttribute('key') else None

        chords = [self.processStructure(x, signature) for x in iterElements(element)]

        if not chords:
            raise ParseException(u"Последовательность %s пуста" % id)

        self.validate(id, chords, signature)

        self.values[id] = Progression(signature, title, chords, key)

    @classmethod
    def validate(cls, id, chords, signature):
        """
        Проверяем, что такт заполнен полностью

        :type id: str or unicode
        :type chords: list(RawChord)
        :rtype: None
        """
        beatsTotal = sum(x.length for x in chords)
        beatsLeft = beatsTotal.shortage(signature)

        if beatsLeft:
            raise ParseException(u'Незаконченный такт в последовательности %s: %s' % (id, beatsLeft))

    @classmethod
    def processStructure(cls, structureElement, signature):
        """
        Генерация элементов RawChord

        Необходимо расчитать размер в долях

        :type structureElement: xml.dom.minidom.Element
        :type signature: Length
        :rtype: None
        """
        length = Length.validator(structureElement.getAttribute('length'), signature)
        chord = structureElement.getAttribute('name')
        if structureElement.tagName == 'chord':
            return RawChord(chord, length)
        else:
            raise ParseException(u"Элемент %s не может содержать элемент %s" % (structureElement.parentNode.tagName, structureElement.tagName))
