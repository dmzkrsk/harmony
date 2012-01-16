# coding=utf-8
from . import BaseTimedStructure
from itertools import product
from ..type.beats import Beat, BeatSheet

class Structure(BaseTimedStructure):
    """
    Парсер структуры в виде маркеров бита
    """
    def preInit(self, declaredLength, structure, **extra):
        """
        Предварительная инициализация

        :type declaredLength: float
        :type structure: xml.dom.minidom.Element
        """
        super(Structure, self).preInit(declaredLength, structure)
        self.beats = BeatSheet()

    def initProgression(self, progression, repeat, repeats, **extra):
        """
        Обработка новой последовательности

        :type progression: Progression
        :type repeat: int
        :type repeats: int
        :rtype: None
        """

        # Расчитываем длину последовательности
        beats = progression.beatCount()
        _beatSize = 60.0 / extra['bpm']

        # Двойной цикл
        # Для каждой доли надо пройти второй цикл по кол-ву долей
        # Так как доля отображается на экране не только во время звучания
        # но и в то время, когда ударение на нее не падает
        for c, b in product(xrange(beats), xrange(progression.signature.numerator)):
            # Номер активной доли
            cn = c % progression.signature.numerator
            beatLabel = Beat(b, progression.signature.numerator, self._position + c * _beatSize,
                cn == b #Доля активна, если совпадают значения
            )
            self.beats.append(beatLabel)

    def initSection(self, section, repeat, repeats):
        pass

    def processChord(self, progression, rawChord):
        pass

    def finishStructure(self):
        """
        Окончание обработки структуры

        Закрываем последовательность
        :rtype: None
        """
        self.beats.close(self._position)
