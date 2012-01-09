# -*- coding: utf-8 -*-
from bisect import bisect_right
from itertools import izip, islice, imap
import struct
import wave

from PIL import Image, ImageDraw, ImageColor

from lib.list import median
import settings

SAMPLES_PER_READ = 50000

class Sampler(object):
    """
    Класс для чтения сэмплов из wav-файла

    Значения сразу группируются и усредняются согласно будущему размеру изображения
    """
    def __init__(self, realX, virtualX, iterator, points):
        """
        :param realX: длина музыкального файла в сэмплах
        :type realX: int
        :param virtualX: ширина будущего изображения
        :type virtualX: int
        :param iterator: итератор, возвращающий сэмплы из файла
        :type iterator: iterator(tuple)
        :param points: точки, по которым строятся разные уровни
        :type points: list(float)
        """

        # Расчитываем номер первого сэмпла на каждой горизонтальный координате будущего рисунка
        starts = [realX * x // virtualX for x in xrange(virtualX)] + [realX]
        # Считать все сэмплы это очень долго
        # Среднее значение уже на нескольких сотен сэмплов будет слабо отличаться от среднего полученного на 10000 сэмплов
        # Чем меньше параметр WAVE_GRAPH_QUALITY тем больше сэмплов мы получим для расчета среднего
        nth = realX // virtualX // settings.WAVE_GRAPH_QUALITY or 1

        self.groups = []
        self.max = 0

        # Двигаемся по горизонтальной координате
        for c, n in izip(starts, starts[1:]):
            # Получаем непустые значения сэмплов
            # Сэмплы приходят в виде кортежа по всем каналам
            # Используем sum для получения значения
            # Берем только каждый nth сэмпл
            # filer, imap и islice работают быстро, так как написаны на C
            #
            # Так как используется итератор, то каждый раз считаем с его начала (0)
            # Когда мы считаем n - c сэмплов, то начало итератора будет опять на следующей секции
            slice = filter(None, imap(sum, islice(iterator, 0, n - c, nth)))

            if slice:
                # Сортируем фрагменты, так как для нахождения медиан нам нужен отсортированый список
                slice = sorted(slice)

                # ищем первое положительное значение
                # нулей в списке уже нет, их отфильтровал filter
                # В итоге slice быстро делится на отдельные последовательности положительных и отрицательных значений
                pPos = bisect_right(slice, 0)
                # Обновляем максимальное абсолютное значение
                self.max = max(-slice[0], slice[-1], self.max)
                # Считаем медианы и добавляем к списку
                self.groups.append(self.calculate(slice, pPos, points))
            else:
                # Если фрагмент пуст (что бывает в начале композиции), то сразу возвращаем нули
                self.groups.append([0, 0] * (len(points) + 1))

    @classmethod
    def calculate(cls, slice, pPos, points):
        """
        Расчет медиан

        :type slice: list(int)
        :type pPos: int
        :type points: list(float)
        :rtype: list
        """
        dots = []
        # Если нет последовательности отрицательных элементов, то не считаем медианы
        if pPos:
            dots.append(slice[0])
            dots.extend(median(slice, 0, pPos, 1 - p) for p in reversed(points))
        else:
            dots.extend([0] * (len(points) + 1))

        l = len(slice)

        # Если нет последовательности положительных элементов, то не считаем медианы
        if pPos == l:
            dots.extend([0] * (len(points) + 1))
        else:
            dots.extend(median(slice, pPos, l - pPos, p) for p in points)
            dots.append(slice[-1])

        return dots

class WaveFile(object):
    """
    Работа с wav-файлами
    """
    def __init__(self, filename):
        """
        :type filename: str or unicode
        """
        self._w = wave.open(filename)
        self.filename = filename

        self._sampleWidth = self._w.getsampwidth()

        if self._sampleWidth < 1 or self._sampleWidth > 2:
            raise ValueError("Only 8 and 16-bit files are supported")

        self._rSymbol = 'bh'[self._sampleWidth-1]

        self.channels = self._w.getnchannels()

        self.wavSize = self._w.getnframes()
        self.length = float(self.wavSize) / self._w.getframerate()

    def readSamples(self):
        """
        Чтение сэмплов из файла

        :rtype: iterator(tuple(int))
        """
        while True:
            # Читаем блок данных
            waveData = self._w.readframes(SAMPLES_PER_READ)
            if not waveData:
                break

            # Определяем количество прочитанных сэмплов
            samplesRead = len(waveData) / self._sampleWidth / self.channels

            # "Распаковываем" байт-данные в последовательность int
            rawData = struct.unpack("<%d%s" % (samplesRead * self.channels, self._rSymbol), waveData)
            # групируем данные в кортежи согласно количеству каналов
            for x in izip(*(iter(rawData),) * self.channels):
                yield x

    def writeWave(self, waveformW, waveformH):
        """
        Запись изображения wav-файла в файл

        :type waveformW: int
        :type waveformH: int
        :return: Lazy-объект для последующей записи в файл
        :rtype: WaveWriter
        """

        # Имя будущего файла
        oFilename = self.filename.rsplit('.', 1)[0] + '.%dx%d.png' % (waveformW, waveformH)
        return WaveWriter(oFilename, self, waveformW, waveformH)

class WaveWriter(object):
    def __init__(self, filename, wavefile, waveformW, waveformH):
        """
        :type filename: str or unicode
        :type wavefile: WaveFile
        :type waveformW: int
        :type waveformH: int
        :rtype:
        """
        self.filename = filename
        self._wf = wavefile
        self.waveformW = waveformW
        self.waveformH = waveformH

    def write(self, colorMap, points):
        """
        Запись изображения wav-файла в файл
        :param colorMap: карта цветов секций
        :type colorMap: list(tuple(float, str))
        :rtype: None
        """
        colorX = [x[0] for x in colorMap]
        colorV = [x[1] for x in colorMap]

        points = sorted(points)
        samplesIterator = self._wf.readSamples()
        sampler = Sampler(self._wf.wavSize, self.waveformW, samplesIterator, points)

        # Лямбда-функция для преобразования времени в горизонтальную координату
        coorTrans = lambda x: self.waveformH - round((x + sampler.max) * self.waveformH / 2 / sampler.max)

        wfImage = Image.new("RGBA", (self.waveformW, self.waveformH))
        wfDraw = ImageDraw.Draw(wfImage)

        # Для каждой горизонтальной координаты...
        for xCoor, dots in enumerate(sampler.groups):
            # ... получаем список вертикальных координат из сэмплера
            dots = [(xCoor, coorTrans(x)) for x in dots]

            # группируем в линии
            lines = izip(dots[:-1], dots[1:])
            lm = len(points)

            # получаем базовый цвет линии согласно секции, в которую попадает текущее время
            colorId = bisect_right(colorX, (xCoor + .5) * self._wf.length / self.waveformW)
            colorHex = colorV[colorId - 1] if colorId else colorV[0]
            color = None if colorHex is None else ImageColor.getrgb(colorHex)

            for ln, line in enumerate(lines):
                # Дополнительно добавляем альфа-канал, согласно "удаленности" линии от центра
                if color is None:
                    alpha = 100 - 50 * abs(ln - lm) / (lm + 1)
                    c = 255, 255, 255, alpha
                else:
                    alpha = 255 - 200 * abs(ln - lm) / (lm + 1)
                    #noinspection PyUnresolvedReferences
                    c = color + (alpha,)
                wfDraw.line(line, c)

        del wfDraw
        # Сохраняем в файл
        with open(self.filename, 'wb') as f:
            wfImage.save(f, 'PNG')
