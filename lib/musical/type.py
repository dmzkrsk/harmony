# coding=utf-8
from song.validator import ValidationException

class Length(object):
    """
    Класс для хранение длины аккорда в долях (1/4, 3/8, ...)
    и арифметических операций
    """

    def __init__(self, numerator, denominator):
        self.numerator = numerator
        self.denominator = denominator

    def __str__(self):
        return '%d/%d' % (self.numerator, self.denominator)

    def rc(self, d):
        """
        Внутренняя функция для перерасчета numerator для нового denominator

        :type d: int
        :rtype: int
        """
        return self.numerator * d /self.denominator

    def __add__(self, other):
        """
        Сумма двух ChordLength

        Предполагаем, что denominator является степенью двойки.
        При нормальной работе программы это так

        :type other: Length
        :rtype: Length
        """

        if other is None:
            return self

        d = max(self.denominator, other.denominator)

        if isinstance(other, int):
            odc = d * other
        else:
            odc = other.rc(d)

        return Length(self.rc(d) + odc, d)

    __radd__ = __add__

    def count(self, other):
        """
        "Деление" длительностей

        :type other: Length
        :rtype: float
        """

        return 1.0 * self.numerator * other.denominator / self.denominator / other.numerator

    def shortage(self, other):
        """
        Расчет ChordLength необходимого для завершения такта указанного через other

        Предполагаем, что denominator является степенью двойки.
        При нормальной работе программы это так
        :type other: Length
        :rtype: Length
        """
        d = max(self.denominator, other.denominator)
        n2 = other.rc(d)
        n1 = self.rc(d) % n2

        if n1:
            return Length(n2 - n1, d)
        else:
            return Length(0, 1)

    def __nonzero__(self):
        """
        Для преобразование в булево значение

        :rtype: bool
        """
        return bool(self.numerator)

    def seconds(self, bpm):
        """
        Длина в четвертях

        :type bpm: float
        :rtype: float
        """
        return 240.0 * self.numerator / self.denominator / bpm

    #noinspection PyTupleAssignmentBalance
    @classmethod
    def validator(cls, value, signature=None):
        """
        Проверка строкового обозначения сигнатуры на соответствие шаблону (4/4, 3/4, 6/8...)

        :type value: unicode
        :rtype: Length
        """
        if not value:
            return Length(4, 4)

        if value == 'bar' and signature is not None:
            return signature

        try:
            b, m = value.split('/')
            b = int(b)
            m = int(m)
            if m in [1, 2, 4, 8, 16, 32, 64, 128] and b > 0:
                return Length(b, m)
        except (AttributeError, ValueError) :
            pass

        raise ValidationException(u'Неверное значение для сигнатуры: %s' % value)
