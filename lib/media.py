# coding=utf-8
from PIL import Image

class Media(object):
    """
    Определение характеристик медиа-файла
    """
    IMAGE = 1
    def __init__(self, filename):
        """
        :type filename: str or unicode
        """
        self.filename = filename
        try:
            im = Image.open(filename)
            self.size = im.size
            self.type = Media.IMAGE
        except IOError, e:
            raise TypeError(u'Неопознанный медиафайл %s: %s' % (filename, e))


