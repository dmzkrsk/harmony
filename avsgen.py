# -*- coding: utf-8 -*-
from operator import itemgetter
import codecs
import sys
from optparse import OptionParser
from lib.media import Media
from options import DOption

from output import avs
from avshelper import subtitlesFromLabels, frameNumber
import settings
from song.reader import SongReader
from song.title import MetaTitle
from song.structure import label, beats
from lib.wavefile import WaveFile

parser = OptionParser(usage="usage: %prog options", option_class=DOption)
parser.add_option('-b', "--background", action="store", type="opacity", dest="background", help="Additional background opacity")
parser.add_option('-x', "--song", action="store", dest="xml", help="XML Song file")
parser.add_option('-w', "--wav", action="store", dest="wav", help="Input WAV file")
parser.add_option("--wmove", action="store", type='float', dest="wmove", help="WAV image scroll", default=1.0)
parser.add_option("--middle", action="store_true", dest="middle", help="No cursor", default=False)
parser.add_option('-s', "--size", action="store", type='dimension', dest="size", help="Output size", default=(640, 480))
parser.add_option("--source", action="store", type='source', dest="source", help="Source image or video", default=None)
parser.add_option('-f', '--fps', action="store", dest="fps",  type='int', help="Resulting video FPS", default=10)
parser.add_option('--font', action="store", dest="font",  help="Font file")

if __name__ == '__main__':
    sys.stderr = codecs.getwriter(sys.stderr.encoding or 'UTF-8')(sys.stderr, errors='replace')

    options, args = parser.parse_args()

    if options.source:
        options.size = options.source.size

    options.wmove = max(1.0, options.wmove)

    # загружаем данные
    wav = WaveFile(options.wav)
    harmony = SongReader(options.xml)
    labels = harmony.getStructureAs(label.Structure)
    beats = harmony.getStructureAs(beats.Structure)

    # сравним размер wav файла и рекомендуемый размер в XML
    #noinspection PyTypeChecker
    if abs(wav.length - harmony.declaredLength) > 1.0 / options.fps:
        print >>sys.stderr, "WAV file length doesn't match one specified in song file"
        sys.exit(10)

    # генерируем звуковую волну картинкой
    wW = int(options.wmove * options.size[0])
    waveWriter = wav.writeWave(wW, options.size[1] / settings.WAVE_FORM_PART)

    # итоговое кол-во кадров в видео
    W, H, wH = options.size[0], options.size[1], options.size[1] / settings.WAVE_FORM_PART
    waveMoving = wW > W
    print '### DECLARATION'
    print avs.Declare('frameCount', int(wav.length * options.fps))
    print avs.Declare('fontName', options.font)
    print avs.Declare('beatColorNormal', avs.Color.hex(settings.BEAT_COLOR_NORMAL))
    print avs.Declare('beatColorActive', avs.Color.hex(settings.BEAT_COLOR_ACTIVE))
    print avs.Declare('W', W)
    print avs.Declare('H', H)
    print avs.Declare('wH', wH)
    print avs.Declare('wW', wW)
    print avs.Declare('waveOpacity', 220)
    print avs.Declare('wavSource', options.wav)
    print avs.Declare('barColor', avs.Color.rgb(255, 255, 255))
    print avs.Declare('commonColor', avs.Color.hex(settings.COMMON_COLOR))
    print '########################################'
    print avs.Declare('wiSource', waveWriter.filename.replace('%dx%d' % (wW, wH), '"+String(wW)+"x"+String(wH)+"'))
    print avs.Declare('beatSize', avs.Var('H/12'))
    print avs.Declare('chordSize', avs.Var('H/4'))
    print avs.Declare('sectionSize', avs.Var('H/12'))
    print avs.Declare('progressionSize', avs.Var('H/18'))
    print avs.Declare('infoSize', avs.Var('H/24'))
    print avs.Declare('commonSize', avs.Var('H/24'))
    print avs.Declare('emptyH', avs.Var('(H-wH) * 1 / 8'))
    print avs.Declare('chordY', avs.Var('0 * emptyH'))
    print avs.Declare('sectionY', avs.Var('4 * emptyH'))
    print avs.Declare('progressionY', avs.Var('5 * emptyH'))
    print avs.Declare('beatY', avs.Var('6 * emptyH'))
    print avs.Declare('infoY', avs.Var('7 * emptyH'))
    print '########################################'
    print
    del W, H, wH

    # главный видеоклип
    mvc = avs.Var(settings.MAIN_VIDEO_CLIP)

    if options.source:
        if options.source.type == Media.IMAGE:
            print settings.MAIN_VIDEO_CLIP + ' = ' + avs.Function('ImageSource',
                options.source.filename,
                start=1,
                end=avs.Var('frameCount'),
                pixel_type = 'RGB32',
                fps = options.fps,
            )
        else:
            print >>sys.stderr, "Unexpected error"
            sys.exit(100)
        # Фон
        if options.background > 0:
            print 'bg = ' + avs.Function('BlankClip', mvc)
            print settings.MAIN_VIDEO_CLIP + ' = ' + avs.Function('Overlay', mvc, avs.Var('bg'), x=0, y=0, opacity=options.background)
    else:
        print settings.MAIN_VIDEO_CLIP + ' = ' + avs.Function('BlankClip',
            length = avs.Var('frameCount'),
            width = avs.Var('W'),
            height = avs.Var('H'),
            pixel_type = 'RGB32',
            fps = options.fps,
        )

    # Аккорды
    subtitlesFromLabels(labels.chords,       options.fps, avs.Var('fontName'), avs.Var('4 * emptyH'), avs.Var('chordSize'),       avs.Var('chordY'))
    # Структура
    subtitlesFromLabels(labels.sections,     options.fps, avs.Var('fontName'), avs.Var('emptyH'),     avs.Var('sectionSize'),     avs.Var('sectionY'))
    # Последовательности
    subtitlesFromLabels(labels.progressions, options.fps, avs.Var('fontName'), avs.Var('emptyH'),     avs.Var('progressionSize'), avs.Var('progressionY'))
    # Инфо
    subtitlesFromLabels(labels.infos,        options.fps, avs.Var('fontName'), avs.Var('emptyH'),     avs.Var('infoSize'),        avs.Var('infoY'))

    # Звездочки маркеры бита
    print avs.Declare(settings.MAIN_VIDEO_CLIP, avs.Var(settings.MAIN_VIDEO_CLIP)) + ' \\'
    for start, end, beat, in sorted(beats.beats.iterTimed(), key=itemgetter(0)):
        print '  .' + avs.Function('Subtitle', beat.title,
            first_frame=frameNumber(start, options.fps),
            last_frame=frameNumber(end, options.fps) - 1,
            font=avs.Var('fontName'),
            size=avs.Var('beatSize'),
            x=avs.Var('W * %d / %d - beatSize / 2' % (2 * beat.position + beat.positions + 3, 4 * beat.positions + 4)),
            y=avs.Var('beatY + emptyH - 1'),
            text_color=avs.Color.hex(beat.color),
            align=1,
        ) + ' \\'
    print

    # Рисуем палку указатель позиции
    print 'bar = ' + avs.Function('BlankClip', width=1, height=avs.Var('wH'), color=avs.Var('barColor'), pixel_type='RGB32')
    # Сохраняем и загружаем картинку звука
    waveWriter.write(
        labels.getColorMap(),
        [.7, .9, .97],
    )
    print 'wave = ' + avs.Function('ImageSource', avs.Var("wiSource"), pixel_type = 'RGB32')
    # Добавляем на главное видео
    if not waveMoving:
        print settings.MAIN_VIDEO_CLIP + ' = ' + avs.Function('Layer', mvc, avs.Var('wave'), 'add', x=0, y=avs.Var('H-wH'), level=avs.Var('waveOpacity'))
    else:
        if options.middle:
            print settings.MAIN_VIDEO_CLIP + ' = ' + avs.Function('Animate', mvc, 0, avs.Var('frameCount') + ' - 1', "Layer",
                avs.Var('wave'), "add", avs.Var('waveOpacity'), avs.Var('W/2'), avs.Var('H-wH'),
                avs.Var('wave'), "add", avs.Var('waveOpacity'), avs.Var('W/2-wW'), avs.Var('H-wH'),
            )
        else:
            print settings.MAIN_VIDEO_CLIP + ' = ' + avs.Function('Animate', mvc, 0, avs.Var('frameCount') + ' - 1', "Layer",
                avs.Var('wave'), "add", avs.Var('waveOpacity'), 0, avs.Var('H-wH'),
                avs.Var('wave'), "add", avs.Var('waveOpacity'), avs.Var('W-wW'), avs.Var('H-wH'),
            )
    # Анимируем указатель
    if waveMoving and options.middle:
        print settings.MAIN_VIDEO_CLIP + ' = ' + avs.Function('Overlay', mvc, avs.Var('bar'), x=avs.Var('W/2'), y=avs.Var('H-wH'))
    else:
        print settings.MAIN_VIDEO_CLIP + ' = ' + avs.Function('Animate', mvc, 0, avs.Var('frameCount') + ' - 1', "Overlay",
            avs.Var('bar'), 0, avs.Var('H-wH'),
            avs.Var('bar'), avs.Var('W'), avs.Var('H-wH'),
        )

    # Загружаем звук
    print 'a = ' + avs.Function('WAVSource', avs.Var("wavSource"))
    # Сводим
    print avs.Function('AudioDub', mvc, avs.Var('a'))
    # Глобальные надписи
    print avs.Function('Subtitle', harmony.buildTitle(MetaTitle).getTitle(),
        y=4,
        first_frame=0,
        last_frame=avs.Var('frameCount'),
        font=avs.Var('fontName'),
        size=avs.Var('commonSize'),
        text_color=avs.Var('commonColor'),
        align=8,
        lsp=1)
