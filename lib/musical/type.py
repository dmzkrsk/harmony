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

    def _rc(self, d):
        """
        Внутренняя функция для перерасчета numerator для нового denominator

        :type d: int
        :rtype: int
        """
        return self.numerator * d /self.denominator

    def __sub__(self, other):
        return self._op(other, False)

    def __add__(self, other):
        return self._op(other, True)

    def _op(self, other, sum):
        """
        Сумма или разность двух ChordLength

        Предполагаем, что denominator является степенью двойки.
        При нормальной работе программы это так

        :type other: Length or int or None
        :type sum: boolean
        :rtype: Length
        """

        if other is None:
            return self

        d = max(self.denominator, other.denominator)

        if isinstance(other, int):
            odc = d * other
        else:
            odc = other._rc(d)

        if sum:
            return Length(self._rc(d) + odc, d)
        else:
            return Length(self._rc(d) - odc, d)

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
        n2 = other._rc(d)
        n1 = self._rc(d) % n2

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

    def __gt__(self, other):
        return self._cmp(other, True, False)

    def __ge__(self, other):
        return self._cmp(other, True, True)

    def __lt__(self, other):
        return self._cmp(other, False, False)

    def __le__(self, other):
        return self._cmp(other, False, True)

    def __eq__(self, other):
        return self._cmp(other, None, True)

    def __ne__(self, other):
        return self._cmp(other, None, False)

    def _cmp(self, other, gt, eq):
        if isinstance(other, float):
            raise ValueError("Cannot compare Length to float")

        d = self._op(other, False)

        if gt is None:
            return bool(d) != eq
        elif not d:
            return eq
        else:
            return (d.numerator > 0) == gt

    @classmethod
    def make_validator(cls, signature=None):
        #noinspection PyTupleAssignmentBalance
        def _validator(value):
            """
            Проверка строкового обозначения сигнатуры на соответствие шаблону (4/4, 3/4, 6/8...)

            :type value: unicode
            :rtype: Length
            """
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
        return _validator

if __name__ == '__main__':
    assert not Length(0, 4)
    assert Length(5, 8)
    assert Length(5,8) > 0
    assert Length(5,8) != 0
    assert Length(5,8) != 1
    assert Length(5,8) != 2
    assert Length(5,8) < 1
    assert Length(8,8) == 1
    assert Length(8,8) != 2
    assert Length(8,8) >= 1
    assert Length(8,8) <= 1
    assert Length(8,8) > 0
    assert Length(8,8) < 2

    assert Length(5,8) == Length(10,16)
    assert Length(5,8) != Length(6,8)
    assert Length(5,8) < Length(6,8)
    assert Length(5,8) > Length(4,8)
    assert Length(5,8) == Length(5,8)
    assert Length(5,8) >= Length(5,8)
    assert Length(5,8) >= Length(10,16)
    assert Length(5,8) <= Length(5,8)
    assert Length(5,8) <= Length(10,16)
    assert Length(0,8) == Length(0, 4)
    assert Length(4,8) == Length(2, 4)

