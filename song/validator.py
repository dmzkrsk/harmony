# -*- coding: utf-8 -*-
"""
Валидаторы типов
"""
import re

_COLOR = re.compile('#([0-9a-f]{2}){3}', re.I)

class ValidationException(Exception):
    """
    Исключение, бросаемое при неудачной валидации
    """
    pass

def year(value):
    """
    Проверка строкового обозначения года на соответствие целому числу

    :type value: unicode
    :rtype: int
    """
    try:
        return int(value)
    except ValueError:
        pass

    raise ValidationException(u'Неверное значение для года: %s' % value)

def bpm(value):
    """
    Проверка строкового обозначения скорости на соответствие положительному числу с плавающей точкой

    :type value: unicode
    :rtype: float
    """
    try:
        t = float(value)
        if t > 0:
            return t
    except ValueError:
        pass

    raise ValidationException(u'Неверное значение для темпа композиции: %s bpm' % value)

def length(value):
    """
    Проверка строкового обозначения длительности композиции на соответствие положительному числу с плавающей точкой

    :type value: unicode
    :rtype: float
    """
    try:
        t = float(value)
        if t > 0:
            return t
    except ValueError:
        pass

    raise ValidationException(u'Неверное значение для длительности композиции: %ss' % value)

def start(value):
    """
    Проверка строкового обозначения начала композиции на соответствие положительному числу с плавающей точкой

    :type value: unicode
    :rtype: float
    """
    try:
        t = float(value)
        if t >= 0:
            return t
    except ValueError:
        pass

    raise ValidationException(u'Неверное значение для начала композиции: %ss' % value)

def repeats(value):
    """
    Проверка строкового обозначения количества повтором на соответствие целое число больше единицы.
    Единица в случае, если значение не указано

    :type value: unicode
    :rtype: int
    """
    if not value:
        return 1

    try:
        v = int(value)
        if v > 1:
            return v
    except ValueError:
        pass

    raise ValidationException(u'Неверное значение для повторов: %s' % value)

def color(value, default):
    """
    Проверка строкового обозначения цвета на соответствие шаблону

    :type value: unicode
    :rtype: unicode
    """
    if not value:
        value = default

    if not _COLOR.match(value):
        raise ValidationException(u'Неверное значение для цвета: %s' % value)

    return value
