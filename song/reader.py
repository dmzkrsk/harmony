# coding= utf-8
from operator import itemgetter
from song.loader import *
import xml.dom.minidom
from song.timemap import ConstantTimeMap, MarkTimeMap
import validator
from lib.musical.validator import key as validator_key

def _metaValue(tag, required, validator=None, default=None):
    """
    Фабричная функция для генерации свойств доступа к элементам раздела meta
    :param tag: Имя тега
    :type tag: str
    :param required: Тег должен существовать, согласно спецификации
    :type required: bool
    :param validator: функция, проверяющая и преобразующая элемент в требуемый тип
    :type validator: function
    :rtype: property
    """
    if validator is None:
        validator = lambda x: x

    def _wrapper(self):
        elements = self._meta.getElementsByTagName(tag)

        if len(elements) > 1:
            raise ParseException(u'Элемент meta не должен содержать более одного элемента %s' % tag)

        if len(elements) == 0 and not required:
            return default

        if len(elements) == 0 and required:
            raise ParseException(u'Элемент meta должен содержать элемент %s' % tag)

        v = self._getText(elements[0])
        return validator(v)

    _wrapper.__name__ = '_f_%s' % tag
    return property(_wrapper)

class SongReader(object):
    """
    Основной класс для разбора XML
    """
    def __init__(self, filename):
        # Парсер XML
        self._dom = xml.dom.minidom.parse(filename)
        # Загружаем корневые объекты
        self._meta = self._oneAndOnly('meta')

        bpm = self._meta.getElementsByTagName('bpm')
        time = self._meta.getElementsByTagName('time')

        if len(bpm) > 1 or len(time) > 1 or len(bpm) + len(time) != 1:
            raise ParseException(u'Элемент meta должен содержать один и только один элемент bpm или time')

        # Находим последовательности и секции
        self._progressions = ProgressionLoader(self._oneAndOnly('progressions')).values
        self._sections = SectionLoader(self._oneAndOnly('sections')).values

        # Загружаем корень структуры
        self._structure = self._oneAndOnly('structure')
        structureStart = getAttr(self._structure, 'start', False, validator.start, 0.0)

        if len(bpm) == 1:
            v = unicode(self._getText(bpm[0]))
            self._timeMap = ConstantTimeMap(structureStart, validator.bpm(v))
        else:
            marks = []
            for mark in time[0].getElementsByTagName('mark'):
                bar = getAttr(mark, 'bar', True, validator.bar)
                timestamp = getAttr(mark, 'timestamp', True, validator.start)
                marks.append((bar, timestamp))
            marks.sort(key=itemgetter(0))

            if len(marks) < 2:
                raise ParseException(u'Элемент time должен содержать от двух элементов mark')

            if not marks[0][0]:
                raise ParseException(u'Начальный элемент mark не может начинаться он нулевого такта')

            timestamps = map(itemgetter(1), marks)
            if any(p > n for p, n in zip(timestamps[:-1], timestamps[1:])):
                raise ParseException(u'Элементы mark должны образовывать возрастающую последовательность')

            self._timeMap = MarkTimeMap(structureStart, marks)

    def _oneAndOnly(self, tag):
        """
        Загружает дочерний тег с требуемым именем и убеждается, что он существует в единственном экземпляре

        :type tag: str
        :rtype: xml.dom.minidom.Element
        """
        elements = self._dom.getElementsByTagName(tag)
        if len(elements) != 1:
            raise ParseException(u'XML-файл должен содержать один и только один элемент %s' % tag)

        return elements[0]

    def _getText(self, *nodelist):
        """
        Текст XML-элемента. Получается комбинацией тектовых блоков

        :type nodelist: list(xml.dom.minidom.NodeList)
        :rtype: str or unicode
        """
        rc = []
        for node in nodelist:
            for c in node.childNodes:
                if c.nodeType == c.TEXT_NODE:
                    rc.append(c.data)
        return ''.join(rc)

    artist = _metaValue('artist', True)
    title = _metaValue('title', True)
    album = _metaValue('album', False)
    year = _metaValue('year', False, validator.year)
    declaredLength = _metaValue('length', True, validator.length)
    key = _metaValue('key', False, validator_key)
    transposition = _metaValue('transposition', False, validator_key)
    comment = _metaValue('comment', False)

    def buildTitle(self, titlebuilder, **kwargs):
        """
        Генерация текстов используя переданный Строитель (DI во всей красе)

        :type titlebuilder: title.Title
        :rtype: title.Title
        """
        return titlebuilder(self, **kwargs)

    #noinspection PyTypeChecker
    def getStructureAs(self, structure):
        """
        Генерация структуры используя переданный строитель струтур (DI во всей красе)

        :type structure: structure.BaseStructure
        :rtype: structure.BaseStructure
        """
        return structure(self._structure, self._sections, self._progressions,
            declaredLength=self.declaredLength, timeMap=self._timeMap,
            key=self.key, transposition=self.transposition
        )
