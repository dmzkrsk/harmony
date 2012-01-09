# coding=utf-8
from itertools import izip
from abc import ABCMeta, abstractmethod

class TimedException(Exception):
    pass

class Timed(object):
    """
    Класс, представляющий объекты с метками времени
    """
    __metaclass__ = ABCMeta

    def __init__(self, start):
        """
        :type start: float
        """
        self.start = start

    @abstractmethod
    def isEmpty(self):
        """
        Проверка объекта на "пустоту"

        :rtype: bool
        """
        return False

class BaseSheet(object):
    """
    Класс, представляющий базовый класс контейнера для Timed
    """
    __metaclass__ = ABCMeta

    def __init__(self):
        self.lastTimestamp = None

    def close(self, lastTimestamp):
        """
        Закрывает объект для записи и ставит последнюю метку

        :type lastTimestamp: float
        :rtype: None
        """
        self.lastTimestamp = lastTimestamp

    def append(self, timed):
        """
        Добавляет объект в коллекцию

        :type timed: Timed
        :rtype: None
        """
        if self.lastTimestamp is not None:
            raise TimedException('Object is closed')
        assert isinstance(timed, Timed), timed.__class__
        self._append(timed)

    def iterTimed(self, skipEmpty=True):
        """
        Итератор по коллекции с вычислением времени окончания

        :type skipEmpty: bool
        :rtype: iterator(Timed)
        """
        if self.lastTimestamp is None:
            raise TimedException('Object is not closed')

        return self._iterTimed(skipEmpty)

    @abstractmethod
    def _append(self, timed):
        """
        Специфичная для класса реализация добавления объекта

        :type timed: Timed
        :rtype: None
        """
        return

    @abstractmethod
    def _iterTimed(self, skipEmpty=True):
        """
        Специфичная для класса реализация итератора
        """
        return

class TimedSheet(BaseSheet):
    def __init__(self):
        super(TimedSheet, self).__init__()
        self.listOfTimed = []

    def _append(self, timed):
        """
        Специфичная для класса реализация добавления объекта

        :type timed: Timed
        :rtype: None
        """
        self.listOfTimed.append(timed)

    def _iterTimed(self, skipEmpty=True):
        """
        Специфичная для класса реализация итератора

        :type skipEmpty: bool
        :rtype: iterator(tuple(float, float, Timed)
        """
        for t, n in izip(self.listOfTimed, self.listOfTimed[1:] + [None]):
            if skipEmpty and t.isEmpty():
                continue

            yield t.start, n.start if n else self.lastTimestamp, t
