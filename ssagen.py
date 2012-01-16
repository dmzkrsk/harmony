# -*- coding: utf-8 -*-
from itertools import izip
from operator import itemgetter
import codecs
import sys
from optparse import OptionParser
from options import DOption

import settings
from output import ssa
from song.reader import SongReader
from song.structure import label, beats
from lib.wavefile import WaveFile
from song.title import MetaTitle

parser = OptionParser(usage="usage: %prog options", option_class=DOption)
parser.add_option('-b', "--background", action="store", type="opacity", dest="background", help="Additional background opacity", default=0)
parser.add_option('-x', "--song", action="store", dest="xml", help="XML Song file")
parser.add_option('-w', "--wav", action="store", dest="wav", help="Input WAV file")
parser.add_option('-s', "--size", action="store", type='dimension', dest="size", help="Output size", default=(640, 480))
parser.add_option('-o', "--offset", action="store", type='float', dest="offset", help="Offset in seconds for video", default=0)
parser.add_option('--font', action="store", dest="font",  help="Font file")

if __name__ == '__main__':
    sys.stderr = codecs.getwriter(sys.stderr.encoding or 'UTF-8')(sys.stderr, errors='replace')

    options, args = parser.parse_args()

    # загружаем данные
    wav = WaveFile(options.wav)
    harmony = SongReader(options.xml)
    labels = harmony.getStructureAs(label.Structure)
    beats = harmony.getStructureAs(beats.Structure)

    # сравним размер wav файла и рекомендуемый размер в XML
    #noinspection PyTypeChecker
    if abs(wav.length - harmony.declaredLength) > .04:
        print >>sys.stderr, "WAV file length doesn't match one specified in song file"
        sys.exit(10)

    # генерируем звуковую волну картинкой
    waveWriter = wav.writeWave(options.size[0], options.size[1] / settings.WAVE_FORM_PART)

    # итоговое кол-во кадров в видео
    W, H, wH = options.size[0], options.size[1], options.size[1] / settings.WAVE_FORM_PART

    # главный видеоклип
    print """[Script Info]
ScriptType: v4.00+
Collisions: Normal
PlayResY: %(height)d
PlayResX: %(width)d
WrapStyle: 1

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding""" % dict(
    height=H, width=W)

    print ssa.Style('BlackBox', options.font, 0, ssa.color(0, 0, 0, 255 * (1 - options.background)), align=7)
    print ssa.Style('Line', options.font, 0, ssa.color(255,255,255), border=0, align=7)
    print ssa.Style('Chords', options.font, H/4, bold=True, align=2)
    print ssa.Style('Sections', options.font, H/12, bold=True)
    print ssa.Style('Progressions', options.font, H/18, bold=True)
    print ssa.Style('Beat', options.font, H/12, bold=True)
    print ssa.Style('Info', options.font, H/24, bold=True)
    print ssa.Style('Common', options.font, H/24, bold=True, align=8)

    print "[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"

    drawBox = "{\p1}m 0 0 l %(width)d 0 %(width)d %(height)d 0 %(height)d{\p0}" % dict(width=W, height=H)
    print ssa.Dialogue(0, wav.length, "BlackBox", 0, 0, drawBox, lineName='BlackBox', layer=0)

    labelslist = [
        (labels.chords, W/2, (H-wH) / 2 - H / 80, 'Chords'),
        (labels.sections, W/2, (H-wH) * 9 /16, 'Sections'),
        (labels.progressions, W/2, (H-wH) * 11 / 16, 'Progressions'),
    ]

    # Аккорды и структура
    for l, x, y, styleName in labelslist:
        for start, end, label in l.iterTimed():
            print ssa.Dialogue(options.offset + start, options.offset + end, styleName, x, y, label.title, ssa.hexColor(label.color, withAlpha=False))
        print

    # Звездочки маркеры бита
    for start, end, beat, in sorted(beats.beats.iterTimed(), key=itemgetter(0)):
        x = W * (2 * beat.position + beat.positions + 3) // (beat.positions + 1) // 4
        print ssa.Dialogue(options.offset + start, options.offset + end, 'Beat', x, (H - wH) * 13 / 16, beat.title, ssa.hexColor(beat.color, withAlpha=False))
    print

    # Анимируем указатель
    xCoorTimeStamps = [x * wav.length / W for x in xrange(W + 1)]
    for xCoor, time in enumerate(izip(xCoorTimeStamps[:-1], xCoorTimeStamps[1:])):
        start, end = time
        line = "{\p1}m %(x)d %(height)d l %(x)d %(wHY)d %(xp)d %(wHY)d %(xp)d %(height)d{\p0} %(x)d %(height)d" % dict(x=xCoor, height=H, wHY=H - wH, xp=xCoor+1)
        print ssa.Dialogue(options.offset + start, options.offset + end, "Line", 0, 0, line, layer=20)

    # Глобальные надписи
    print ssa.Dialogue(0, wav.length, 'Common', W/2, H/80, '{\\q1}' + harmony.buildTitle(MetaTitle, upperCase=True).getTitle(), ssa.color(255, 255, 255))
    #noinspection PyTypeChecker
    print ssa.Dialogue(options.offset, options.offset + harmony.declaredLength, 'Info', W/2, (H-wH) * 15 /16, '%d bpm | %s' % (int(round(harmony.bpm)), harmony.transposition or harmony.key), ssa.color(255, 255, 255))
