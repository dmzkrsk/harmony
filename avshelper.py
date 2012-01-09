# coding=utf-8
from output import avs
import settings

def frameNumber(time, fps):
    """
    Номер кадра

    :type time: float
    :type fps: int
    :rtype: int
    """
    return int(round(time * fps))

def emptyBar(empty_bar, height):
    return avs.Function('BlankClip', avs.Var(empty_bar), height=height) + ' \\'

def subtitlesFromLabels(clip, empty_bar, labels, fps, align, font, height, size, overlayX, overlayY):
    subtitles = ((frameNumber(start, fps), frameNumber(end, fps), label.title, label.color) \
        for start, end, label in labels.iterTimed())

    print clip + ' = ' + emptyBar(empty_bar, height)
    for start, end, title, color in subtitles:
        print '  .' + avs.Function('Subtitle', title,
            first_frame=start,
            last_frame=end - 1,
            font=font,
            size=size,
            text_color=avs.Color.hex(color),
            align=align
        ) + ' \\'

    print
    print settings.MAIN_VIDEO_CLIP +' = ' + avs.Function('Overlay', avs.Var(settings.MAIN_VIDEO_CLIP), avs.Var(clip), x=overlayX, y=overlayY)
