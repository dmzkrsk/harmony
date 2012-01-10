# coding=utf-8
"""
Вспомогательные функции для генерации avisynth-скриптов
"""
import re

def wrapArgs(v):
    """
    Отображение объекта в строку
    Строки окружаются кавычками
    Другие объекты преобразуются в строки согласно их методам __str__

    :type v: object
    :rtype: str
    """
    if isinstance(v, str):
        return '"%s"' % v
    elif isinstance(v, unicode):
        return '"%s"' % v.encode('utf-8')
    else:
        return str(v)

class Var(object):
    """
    Обертка для переменной -- текст в переменной не окружается кавычками при записи в скрипт
    """
    def __init__(self, name):
        """
        :type name: str or unicode or Var
        """
        self.name = name

    def __str__(self):
        """
        :rtype: str
        """
        return self.name

    def __repr__(self):
        return '<Var: %s>' % self.name

    def __radd__(self, other):
        """
        :type other: str or Var
        :rtype: Var
        """
        return other + self.name

    def __add__(self, other):
        """
        :type other: str or Var
        :rtype: Var
        """
        return Var(self.name + other)

class Color(object):
    """
    Генератор цветов для avisynth

    Цвет задается в hex-строке или rgb-кортеже после чего преобразовывается в Var
    """
    HEX = re.compile('[#$]?([0-9a-fA-F]{6})([0-9a-fA-F]{2})?', re.I)

    @classmethod
    def rgb(cls, r, g, b):
        """
        Создание цвета из кортежа RGB

        :type r: int
        :type g: int
        :type b: int
        :rtype: Var
        """
        return Var('$%02x%02x%02x' % (r, g, b))

    @classmethod
    def hex(cls, hexval):
        """
        Создание цвета из hex-строки

        :type hexval: str or unicode
        :rtype: Var
        """
        m = cls.HEX.match(str(hexval))
        if m:
            return Var('$' + m.group(1).lower())

        raise ValueError('Invalid color: %s' % hexval)

def Function(name, *args, **kwargs):
    """
    Генератор функций

    :param name: Название функции
    :type name: str
    :param args: последовательные аргументы
    :type args: list(object)
    :param kwargs: именованные аргументы
    :type kwargs: dict
    :rtype: str
    """
    fArgs = [wrapArgs(x) for x in args]
    fArgs.extend('%s=%s' % (k, wrapArgs(v)) for k, v in kwargs.iteritems())
    return '%s(%s)' % (name, ', '.join(fArgs))

def Declare(name, value):
    """
    Генератор объявления переменной

    :type name: str
    :type value: object
    :rtype: str
    """
    return '%s = %s' % (Var(name), wrapArgs(value))