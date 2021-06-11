import builtins
import os
import random
import typing as tp

import xonsh.lazyasd as xl
from xonsh.prompt.base import ParsedTokens, _ParsedToken

GRAY = "#273746"
BLUE = "#004C99"
GIT_COLOR = "#e94e31"
LIGHT_GREEN = "#afd700"
PROMPT_FIELD_COLORS_DEFAULT = {
    "cwd": ("INTENSE_WHITE", "CYAN"),
    "gitstatus": ("INTENSE_WHITE", "BLACK"),
    "gitstatus_pl": ("INTENSE_WHITE", GIT_COLOR),
    "ret_code": ("INTENSE_WHITE", "RED"),
    "full_env_name": ("INTENSE_WHITE", LIGHT_GREEN),
    "hostname": ("INTENSE_WHITE", BLUE),
    "localtime": ("#DAF7A6", "black"),
}


@xl.lazyobject
def PROMPT_FIELD_COLORS():
    return builtins.__xonsh__.env.get(
        "PROMPT_FIELD_COLORS", PROMPT_FIELD_COLORS_DEFAULT
    )


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


@xl.lazyobject
def _POWERLINE_MODE_DEFAULT():
    return random.choice(list(modes))


class Section(tp.NamedTuple):
    line: str
    field: tp.Optional[str]
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


@xl.lazyobject
def POWERLINE_SYMBOLS():
    mode = builtins.__xonsh__.env.get("POWERLINE_MODE", _POWERLINE_MODE_DEFAULT)
    return modes[mode]


def _prompt_builder(tokens: tp.List[Section], right=False):
    SEP, THIN, PL_RSEP, _ = POWERLINE_SYMBOLS

    for i, sec in enumerate(tokens):
        first = i == 0

        tok_value = sec.line
        if sec.field == "cwd":
            tok_value = tok_value.replace(os.sep, THIN)

        if right:
            yield "{%s}%s{BACKGROUND_%s}{%s}%s" % (
                sec.bg,
                PL_RSEP,
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
    for tok in tokens:
        if not tok.value:  # skip empty strings
            continue
        args = PROMPT_FIELD_COLORS.get(tok.field, ("white", GRAY))
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
    prompt = builtins.__xonsh__.env["PROMPT"]
    rprompt = builtins.__xonsh__.env["RIGHT_PROMPT"]
    if container.template in {prompt, rprompt}:
        # it is $PROMPT
        is_right = container.template == rprompt
        return os.linesep.join(
            [
                prompt_builder(line, right=is_right)
                for line in split_by_lines(container.tokens)
            ]
        )
    # for title
    return "".join([c.value for c in container.tokens])


builtins.__xonsh__.env["PROMPT_TOKENS_FORMATTER"] = process_prompt_tokens
