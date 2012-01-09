# coding=utf-8
from math import floor, ceil

def median(l, offset, length, p=.5):
    """
    Выбор значения из сортированного списка

    Поиск происходит в l[offset:offset+length]
    При p=0 возвращается первый элемент
    При p=1 -- последний
    Если p указывает между двумя элементами списка, то берется средневзвешенное

    :type offset: int
    :type length: int
    :type p: float
    """
    sp = p * length - .5
    left = floor(sp)
    right = ceil(sp)

    if left < 0:
        return l[offset]
    elif right > length - 1:
        return l[offset + length - 1]
    else:
        lv = l[int(left) + offset]
        rv = l[int(right) + offset]
        return lv if lv == rv else (right - sp) * lv + (sp - left) * rv
