# coding=utf-8
from abc import ABCMeta, abstractmethod

class Title(object):
    """
    Базовый класс генератора текстов из SongReader
    """
    __metaclass__ = ABCMeta

    def __init__(self, loader, **kwargs):
        """
        :type loader: SongReader
        """
        self._loader = loader
        self._kwargs = kwargs

    @abstractmethod
    def getTitle(self):
        """
        Специфичный для класса генератор текста
        :rtype: unicode
        """
        return None

class AlbumTitle(Title):
    """
    Генератор названия альбома. Даже с номером года, если есть
    """
    def getTitle(self):
        """
        :rtype: unicode
        """
        #noinspection PyStringFormat
        return u'%s (%d)' % (self._loader.album, self._loader.year) if self._loader.year and self._loader.album else self._loader.album

class MetaTitle(Title):
    """
    Генератор заголовка
    """
    def getTitle(self):
        """
        :rtype: unicode
        """
        title = u'%s - %s' % (self._loader.artist, self._loader.title)
        album = AlbumTitle(self._loader).getTitle()

        if album:
            title += u' (%s)' % album

        sep = u'\\N' if self._kwargs.get('upperCase', False) else u'\\n'

        if self._loader.comment:
            #noinspection PyTypeChecker
            title += sep + self._loader.comment
        return title
