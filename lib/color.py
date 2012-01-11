# coding=utf-8
from colorsys import hsv_to_rgb
import random

class ColorGeneratorException(Exception):
    pass

def hsv2hex(h, l, s):
    """
    Преобразует цвет из пространства HSV в hex-строку
    :type h: float
    :type l: float
    :type s: float
    :rtype: str
    """
    r, g, b = hsv_to_rgb(h, l, s)
    return '#%02x%02x%02x' % (256*r, 256*g, 256*b)

class RandomColor(object):
    """
    Объект-заглушка для хранения цвета, который будет сгенерирован при попытке взять строковое значение
    """
    def __init__(self, key, factory):
        """
        :type key: object
        :type factory: RandomColorGenerator
        """
        self._key = key
        self._factory = factory

    def __eq__(self, other):
        """
        :type other: RandomColor
        """
        return self._key == other._key and self._factory == other._factory

    def __str__(self):
        return self._factory._color(self._key)

class RandomColorGenerator(object):
    """
    Генератор случайных цветов.

    Цвета регистрируются при попытке записи в __getitem__
    Генерация происходит при вызове generateColors. После этого регистрация новых цветов невозможна
    Цвета генерируются равномерно по знаениям HUE, плюс немного случайности
    """
    def __init__(self):
        self.colors = {}
        self.colorMap = None

    def __getitem__(self, item):
        """
        :type item: object
        :rtype: RandomColor
        """
        if self.colorMap is not None:
            raise ColorGeneratorException('Object is closed')
        self.colors[item] = None
        return RandomColor(item, self)

    def generateColors(self):
        """
        Генерация цветов

        :rtype: None
        """
        colorsCount = len(self.colors)
        self.colorMap = {}
        keys = self.colors.keys()
        random.shuffle(keys)
        start = random.uniform(-.5/colorsCount, .5 / colorsCount)
        for colorIndex, key in enumerate(keys):
            color = hsv2hex(
                (1. + start + float(colorIndex)/colorsCount
                    + random.uniform(-.25/colorsCount, .25/colorsCount)) % 1.0,
                random.uniform(.6,.8),
                random.uniform(.75,.9)
            )

            self.colorMap[key] = color

    def _color(self, key):
        """
        :type key: object
        :rtype: str
        """
        if self.colorMap is None:
            self.generateColors()

        return self.colorMap[key]