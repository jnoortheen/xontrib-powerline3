from colorsys import rgb_to_hsv, hsv_to_rgb, rgb_to_hls, hls_to_rgb


class Colors:
    """some named color codes"""

    # taken from - https://www.w3schools.com/colors/colors_trends.asp
    CYAN = "CYAN"
    GREEN = "#88B04B"  # light green
    EMERALD = "#009B77"  # greenish
    GRAY = "#181818"
    BLUE = "#34568B"
    ORANGE = "#FF6F61"
    BROWN = "#955251"
    ROSE = "#F7CAC9"
    PINK = "#B565A7"
    SERENE = "#92A8D1"  # bluish
    YELLOW = "#f3e0be"
    SAND = "#DFCFBE"  # light yellowish
    VIOLET = "#6B5B95"
    WHITE = "INTENSE_WHITE"
    RED = "RED"


def to_rgb(hx: str):
    from xonsh.color_tools import BASE_XONSH_COLORS

    if hx in BASE_XONSH_COLORS:
        return BASE_XONSH_COLORS[hx]
    return tuple(int(hx[i : i + 2], 16) for i in (0, 2, 4))


def get_lumina(hx: str):
    """for the hex color determine the perceived luminance"""
    R, G, B = to_rgb(hx)
    return (0.2126 * R) + (0.7152 * G) + (0.0722 * B)


def get_contrast_color(hx: str):
    lumina = get_lumina(hx)
    if lumina < 0.5:
        # bright bg -> black fg
        return Colors.GRAY
    return Colors.WHITE
