# coding=utf-8
from bisect import bisect_right
from operator import itemgetter

class ConstantTimeMap(object):
    """
    Перевод номера такта (дробного) в секунды

    Используется bpm. Линейная интерполяция
    """
    def __init__(self, start, bpm):
        """
        :type start: float
        :type bpm: float
        """
        self._start = start
        self._bpm = bpm

    def __call__(self, bar):
        """
        :type bar: lib.musical.type.Length
        :rtype: float
        """
        return (bar - 1).seconds(self._bpm) + self._start

    #noinspection PyUnusedLocal
    def bpm(self, bar):
        return self._bpm

class MarkTimeMap(object):
    """
    Перевод номера такта (дробного) в секунды

    Используется карта времени. Интерполяция отрезками
    """

    def __init__(self, start, marks):
        """
        :type start: float
        :type marks: list
        """
        mmarks = [(1, start)] + marks

        self._mk = map(itemgetter(0), mmarks)
        self._mv = map(itemgetter(1), mmarks)
        self._l = len(marks)

        self._bpm = [
            240 * (m1[0] - m0[0]) / (m1[1] - m0[1])
            for m0, m1 in zip(mmarks[:-1], mmarks[1:])
        ]

        self._bpm.append(self._bpm[-1])

    def _i(self, bar):
        """
        :type bar: lib.musical.type.Length
        :rtype: int
        """
        return bisect_right(self._mk, bar)

    def __call__(self, bar):
        """
        :type bar: lib.musical.type.Length
        :rtype: float
        """
        i = self._i(bar)

        v0 = bar - self._mk[i-1]
        s0 = self._mv[i-1]

        return s0 + v0.seconds(self._bpm[i-1])

    def bpm(self, bar):
        i = self._i(bar)
        return self._bpm[i-1]
