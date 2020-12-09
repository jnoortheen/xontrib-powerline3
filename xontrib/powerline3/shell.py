"""Some useful functions to wrap fields with color"""
import typing as tp


def _format_color(color: tp.Optional[str], bold, slow_blink):
    color_sects = []
    if color:
        color_sects.append(color.upper())
    if bold:
        color_sects = ["BOLD_"] + color_sects
    if slow_blink:
        color_sects = ["SLOWBLINK_"] + color_sects
    return "".join(color_sects)


def _format_style(color, bg_color):
    stls = []
    if bg_color:
        stls.append("BACKGROUND_" + bg_color)
    if color:
        stls.append(color)

    return "".join([("{{%s}}" % s) for s in stls])


def with_color(
    field: str,
    color: str = None,
    bg_color=None,
    bold=False,
    slow_blink=False,
    prefix: str = "",
    suffix: str = "",
):
    """
    >>> with_color("user")
    '{user:{}}'
    >>> with_color("user", 'red')
    '{user:{{RED}}{}{{RESET}}}'
    """
    color = _format_color(color, bold, slow_blink)
    style = _format_style(color, bg_color)

    prefix = "%s%s" % (style, prefix)
    suffix = "%s%s" % (suffix, "{{RESET}}" if style else "")
    return "{%s:%s{}%s}" % (field, prefix, suffix)
