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


class Section(tp.NamedTuple):
    line: str
    field: "str|None" = None
    fg: str = ""
    bg: str = ""


def _build_left_section(
    sec: Section,
    first: bool,
    tok_value: str,
    SEP: str,
    next_sec: tp.Optional[Section],
) -> tp.Iterator[str]:
    if first:
        if sec.bg:
            yield "{BACKGROUND_%s}" % sec.bg
    if sec.fg:
        yield "{%s}" % sec.fg

    yield tok_value
    if next_sec is None:
        yield "{RESET}"
        if sec.bg:
            yield "{%s}" % sec.bg
        yield "%s{RESET}" % SEP
    else:
        if next_sec.bg:
            yield "{BACKGROUND_%s}" % next_sec.bg
        if sec.bg:
            yield "{%s}" % sec.bg
        yield SEP


@functools.lru_cache(None)
def get_pl_symbols() -> "tuple[str, str, str]":
    mode = XSH.env.get("POWERLINE_MODE", get_a_powerline_mode())
    return modes[mode][:3]


def thin_join(parts):
    _, THIN, _ = get_pl_symbols()

    return THIN.join(parts)


def _prompt_builder(tokens: tp.List[Section], right=False):
    SEP, THIN, RSEP = get_pl_symbols()

    for i, sec in enumerate(tokens):
        first = i == 0

        tok_value = sec.line

        if right:
            yield "{%s}%s{BACKGROUND_%s}{%s}%s" % (
                sec.bg,
                RSEP,
                sec.bg,
                sec.fg,
                tok_value,
            )

        else:
            next_sec = tokens[i + 1] if i < len(tokens) - 1 else None
            yield from _build_left_section(sec, first, tok_value, SEP, next_sec)


def prompt_builder(tokens: tp.List[Section], right=False):
    return "".join(_prompt_builder(tokens, right))


def create_sections(tokens: tp.List[_ParsedToken]):
    from xontrib_powerline3.fields import get_pl_colors

    for tok in tokens:
        if not tok.value:  # skip empty strings
            continue
        args = get_pl_colors(tok.field)
        yield Section(tok.value, tok.field, *[a.upper() for a in args])


def split_by_lines(tokens: tp.List[_ParsedToken]):
    line = []
    for tok in tokens:
        if tok.value == os.linesep:
            yield list(create_sections(line))
            line.clear()
        else:
            line.append(tok)
    yield list(create_sections(line))


def process_prompt_tokens(container: ParsedTokens) -> str:
    prompt = XSH.env["PROMPT"]
    rprompt = XSH.env["RIGHT_PROMPT"]
    if container.template in {prompt, rprompt}:
        is_right = container.template == rprompt
        return os.linesep.join(
            [
                prompt_builder(line, right=is_right)
                for line in split_by_lines(container.tokens)
            ]
        )
    # for title
    return "".join([c.value for c in container.tokens])
