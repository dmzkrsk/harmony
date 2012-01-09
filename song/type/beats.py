# coding=utf-8
from label import Label
from lib.timed import BaseSheet
import settings

class Beat(Label):
    """
    Класс метки бита

    В отличии от обычных меток его надо позиционировать по горизонтали
    Для этого дополнительно хранятся поля position/positions
    """

    def __init__(self, position, positions, start, active):
        """
        :type position: int
        :type positions: int
        :type start: float
        :param active: Метка активности в данный момент бита
        :type active: bool
        """
        super(Beat, self).__init__(str(position + 1), start, settings.BEAT_COLOR_ACTIVE if active else settings.BEAT_COLOR_NORMAL)
        self.position = position
        self.positions = positions

    def isEmpty(self):
        """
        Метка бита никогда не пустует

        :rtype: bool
        """
        return False

class BeatSheet(BaseSheet):
    """
    Контейнер для меток бита

    Место по-горизонтали, на которое выводится метка зависит не только от номера бита,
    но и от текущей сигнатуры. Первая доля в 3/4 и в 4/4 будут занимать разное положение
    при выводе на экран

    Из-за этого структура timedGroups получается сложной

    tuple(
        верхняя цифра сигнатуры,
        tuple(
            номер доли,
            list(доли)
        )
    )
    """
    def __init__(self):
        super(BeatSheet, self).__init__()
        self.timedGroups = []

    def _append(self, beat):
        """
        Специфичная для класса реализация добавления объекта

        :type beat: Beat
        :rtype: None
        """
        assert isinstance(beat, Beat), beat.__class__

        # Если изменилась сигнатура, то начинаем новый раздел timedGroups
        if not self.timedGroups or self.timedGroups[-1][0] != beat.positions:
            # Сразу создаем все возможные в будущем номера долей
            rbeats = [(x, [beat] if x == beat.position else []) for x in xrange(beat.positions)]
            self.timedGroups.append((beat.positions, rbeats))
            return

        # Работаем с текущей сигнатурой
        li = self.timedGroups[-1][1]
        # Берем список предыдущих меток для этой доли
        blist = li[beat.position][1]
        # Если состояние изменилось, то добавляем новую метку
        # В противном случае все "склеится" автоматов в iterTimed
        if not blist or blist[-1].color != beat.color:
            blist.append(beat)

    def _iterTimed(self, skipEmpty=True):
        """
        Специфичная для класса реализация итератора

        Обычно метка выводится на экран до появления следующей
        Но метки долей на экране присутствуют во множественном числе
        Исчезает метка только, если появляется новая НА ЕЕ МЕСТЕ
        или заканчивается действие сигнатуры
        или заканчивается композиция

        В итераторе надо это все учесть

        :type skipEmpty:
        :rtype: iterator(tuple(float, float, Timed)
        """
        # Цикл по всем группам
        signatureSections = len(self.timedGroups)
        for signatureSection in xrange(signatureSections):
            # Время окончания группы: начало следующей группы или конец композиции
            nextSectionTimeStamp = self.timedGroups[signatureSection + 1][1][0][1][0].start if signatureSection + 1 < signatureSections else self.lastTimestamp
            # Цикл по всем долям
            beatsPositions = len(self.timedGroups[signatureSection][1])
            for beatsPosition in xrange(beatsPositions):
                # Цикл по всем сменам меток
                beatPositions = len(self.timedGroups[signatureSection][1][beatsPosition][1])
                for beatPosition in xrange(beatPositions):
                    beat = self.timedGroups[signatureSection][1][beatsPosition][1][beatPosition]
                    # Время окончания метки: начало следующей метки С ЭТОЙ ЖЕ ДОЛЕЙ или начало следующей группы
                    nextBeatTimestamp = self.timedGroups[signatureSection][1][beatsPosition][1][beatPosition + 1].start if beatPosition + 1 < beatPositions else nextSectionTimeStamp

                    yield beat.start, nextBeatTimestamp, beat
