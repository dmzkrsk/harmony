# coding=utf-8
from copy import copy
from optparse import OptionValueError, Option
from lib.media import Media

#noinspection PyUnusedLocal
def check_dimension(option, opt, value):
    try:
        w, h = value.split('x')
        return int(w), int(h)
    except ValueError:
        raise OptionValueError(
            "option %s: invalid dimension value: %r" % (opt, value))

#noinspection PyUnusedLocal
def check_source(option, opt, value):
    try:
        return Media(value)
    except TypeError, e:
        raise OptionValueError(
            "option %s: invalid source value: %r" % (opt, value))

#noinspection PyUnusedLocal
def check_opacity(options, opt, value):
    try:
        v = float(value)
        if 0 <= v <= 1:
            return v
    except ValueError:
        pass

    raise OptionValueError("option %s: invalid opacity value: %r" % (opt, value))

#noinspection PyClassicStyleClass
class DOption (Option):
    TYPES = Option.TYPES + ("dimension", "source", "opacity")
    TYPE_CHECKER = copy(Option.TYPE_CHECKER)
    TYPE_CHECKER["dimension"] = check_dimension
    TYPE_CHECKER["source"] = check_source
    TYPE_CHECKER["opacity"] = check_opacity
