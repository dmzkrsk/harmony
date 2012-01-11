# coding=utf-8
"""
Вспомогательные функции для генерации ssa-скриптов
"""
import os

def color(r, g, b, a=0):
    return "%(a)02X%(b)02X%(g)02X%(r)02X" % locals()

WHITE = color(255, 255, 255)

def timeStamp(seconds):
    """
    Время в формате SSA

    :type seconds: float
    :rtype: str
    """

    cents = int(round(seconds * 100))

    hours = cents // (60*60*100)
    cents %= 60*60*100
    minutes = cents // (60*100)
    cents %= 60*100
    seconds = cents // 100
    cents %= 100
    return "%i:%02i:%02i.%02i" % (hours, minutes, seconds, cents)

def hexColor(color, alpha=0, withAlpha=True):
    """
    Преобразование цвета из HTML в SSA

    :type color: str or unicode
    :type alpha: int
    :rtype: str
    """

    color = str(color).upper()
    return ("%02X" % alpha if withAlpha else '') + color[-6:-4] + color[-4:-2] + color[-2:]

def colorTag(color):
    """
    Цвет в теге

    :type color: str or None
    :rtype: str
    """

    if not color:
        return ''

    return "{\c&H%s&}" % color

def Dialogue(startTime, endTime, styleName, x, y, text, color=None, lineName="", layer=10):
    """
    Строчка диалога

    :type startTime: float
    :type endTime: float
    :type styleName: str
    :type lineName: str
    :type text: object
    :type color: str or None
    :type x: int
    :type y: int
    :rtype: str
    """
    if isinstance(text, unicode):
        text = text.encode('utf-8')
    else:
        text = str(text)

    return "Dialogue: %(layer)d,%(start)s,%(end)s,%(style)s,%(name)s,0000,0000,0000,,%(colorTag)s%(posTag)s%(text)s" % dict(
        layer=layer,
        start=timeStamp(startTime),
        end=timeStamp(endTime),
        style=styleName,
        name=lineName,
        text=text,
        posTag='{\pos(%d,%d)}' % (x, y),
        colorTag=colorTag(color),
    )

def Style(name, fontName, fontSize, primaryColour=WHITE, border=1.6, align=5, bold=False):
    """
    Строчка стиля

    :type name: str
    :type fontName: str or unicode
    :type fontSize: int
    :type primaryColour: str
    :type bold: bool
    :type align: int
    :rtype: str
    """

    #Style: Chords,%(font)s,%(chordSize)d,&H00FFFFFF,,-1,

    return "Style: %(name)s,%(fontName)s,%(fontSize)d,&H%(pcolor)s,&H00000000,&H66000000,&H66000000,%(bold)d,0,0,0,100,100,0,0,1,%(border).1f,0,%(align)d,0,0,0,0" % dict(
        name=name,
        fontName=fontName,
        fontSize=fontSize,
        border=border,
        pcolor=primaryColour,
        bold=-1 if bold else 0,
        align=align,
    )

def Picture(startTime, endTime, x, y, path, lineName="", layer=10):
    """
    Вставка изображений
    """
    return "Picture: %(layer)d,%(start)s,%(end)s,,%(name)s,%(x)04d,0000,%(y)04d,,%(path)s" % dict(
        layer=layer,
        start=timeStamp(startTime),
        end=timeStamp(endTime),
        name=lineName,
        path=os.path.abspath(path),
        x=x,
        y=y
    )
