# coding=utf-8
from . import KEY
from song.validator import ValidationException

def key(value):
    """
    Проверка строкового обозначения тональности на соответствие шаблону

    :type value: unicode
    :rtype: unicode
    """
    if not KEY.match(value):
        raise ValidationException(u'Неверное значение для тональности: %s' % value)

    return value
