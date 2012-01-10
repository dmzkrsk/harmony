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

def subtitlesFromLabels(labels, fps, font, height, fontSize, overlayY):
    subtitles = ((frameNumber(start, fps), frameNumber(end, fps), label.title, label.color) \
        for start, end, label in labels.iterTimed())

    print avs.Declare(settings.MAIN_VIDEO_CLIP, avs.Var(settings.MAIN_VIDEO_CLIP)) + ' \\'
    for start, end, title, color in subtitles:
        print '  .' + avs.Function('Subtitle', title,
            first_frame=start,
            last_frame=end - 1,
            y=avs.Var('%s + %s - 1' % (overlayY, height)),
            font=font,
            size=fontSize,
            text_color=avs.Color.hex(color),
            align=2
        ) + ' \\'

    print
