import dataclasses

import functools

import os
import random
import typing as tp

from xonsh.prompt.base import ParsedTokens, _ParsedToken
from xonsh.built_ins import XSH


# https://www.nerdfonts.com/cheat-sheet?set=nf-ple-
modes = {
    "powerline": "",  # \uE0b0
    "round": "",  # \uE0b4
    "down": "",  # \uE0b8
    "up": "",  # \uE0bc
    "flame": "",  # \ue0c0
    "squares": "",  # \ue0c4
    "ruiny": "",  # \ue0c8
    "lego": "",  # \ue0ce
    "trapezoid": "",  # \ue0d2
    "honeycomb": "",  # \ue0cc
}


@functools.lru_cache(None)
def get_a_powerline_mode():
    return random.choice(list(modes))


@dataclasses.dataclass
class Section:
    line: str
    fg: str = ""
    bg: str = ""
    pl_color: str = ""


@functools.lru_cache(None)
def get_pl_symbols() -> "tuple[str, str, str]":
    mode = XSH.env.get("POWERLINE_MODE", get_a_powerline_mode())
    return modes[mode][:3]


def thin_join(parts):
    _, THIN, _ = get_pl_symbols()

    return THIN.join(parts)


def format_right_prompt(sections: tp.List[Section], sep: str):
    for sec in sections:
        if sec.bg:
            yield "{%s}%s{BACKGROUND_%s}{%s}%s" % (
                sec.bg,
                sep,
                sec.bg,
                sec.fg,
                sec.line,
            )
        else:
            yield sec.line


def format_prompt(sects, sep):
    prev = None
    for sec in sects:
        if sec.bg:
            if (prev is None) or (not prev.bg):
                yield "{BACKGROUND_%s}" % sec.bg
            if sec.fg:
                yield "{%s}" % sec.fg

        yield sec.line

        if sec.bg:
            if sec.pl_color:
                yield "{BACKGROUND_%s}" % sec.pl_color
            else:
                yield "{RESET}"
            yield "{%s}" % sec.bg
            yield sep
            if not sec.pl_color:
                yield "{RESET}"
        prev = sec


def split_by_lines(tokens: tp.List[_ParsedToken]):
    line_toks = []
    for tok in tokens:
        if tok.value == os.linesep:
            yield line_toks
            line_toks.clear()
        else:
            line_toks.append(tok)
    yield line_toks


def render_prompt_lines(tokens, is_right=False):
    from xontrib_powerline3.fields import get_pl_colors

    sep, _, rsep = get_pl_symbols()

    for line_toks in split_by_lines(tokens):

        def fill_sections():
            prev = ""
            for tok in reversed(line_toks):
                if not tok.value:
                    continue
                fg, bg = list(map(str.upper, get_pl_colors(tok.field)))
                yield Section(tok.value, fg, bg, pl_color=prev)
                prev = bg

        sects = list(fill_sections())
        sects.reverse()

        if is_right:
            parts = format_right_prompt(sects, rsep)
        else:
            parts = format_prompt(sects, sep)
        yield "".join(parts)


def process_prompt_tokens(container: ParsedTokens) -> str:
    prompt = XSH.env["PROMPT"]
    rprompt = XSH.env["RIGHT_PROMPT"]
    if container.template in {prompt, rprompt}:
        is_right = container.template == rprompt
        return os.linesep.join(render_prompt_lines(container.tokens, is_right))
    # for title
    return "".join([c.value for c in container.tokens])
