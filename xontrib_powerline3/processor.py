import builtins
import os
import random
import typing as tp

import xonsh.lazyasd as xl
from xonsh.prompt.base import ParsedTokens, _ParsedToken

GRAY = "#273746"
BLUE = "#004C99"
PROMPT_FIELD_COLORS_DEFAULT = {
    "cwd": ("WHITE", "CYAN"),
    "gitstatus": ("WHITE", "BLACK"),
    "ret_code": ("WHITE", "RED"),
    "full_env_name": ("white", "green"),
    "hostname": ("white", BLUE),
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
    # "honeycomb": "",  # \ue0cc
}


@xl.lazyobject
def POWERLINE_MODE_DEFAULT():
    return random.choice(list(modes))


class Section(tp.NamedTuple):
    line: str
    field: tp.Optional[str]
    fg: str = ""
    bg: str = ""


def prompt_builder(tokens: tp.List[Section], right=False):
    size = len(tokens)
    prompt = []
    mode = builtins.__xonsh__.env.get("POWERLINE_MODE", POWERLINE_MODE_DEFAULT)
    SEP, THIN, PL_RSEP, _ = modes[mode]

    for i, sec in enumerate(tokens):
        last = i == size - 1
        first = i == 0

        tok_value = sec.line
        if sec.field == "cwd":
            tok_value = tok_value.replace(os.sep, THIN)

        if right:
            prompt.append(
                "{%s}%s{BACKGROUND_%s}{%s}%s"
                % (sec.bg, PL_RSEP, sec.bg, sec.fg, tok_value)
            )
        else:
            if first:
                if sec.bg:
                    prompt.append("{BACKGROUND_%s}" % sec.bg)
            if sec.fg:
                prompt.append("{%s}" % sec.fg)

            prompt.append(tok_value)
            if last:
                prompt.append("{RESET}")
                if sec.bg:
                    prompt.append("{%s}" % sec.bg)
                prompt.append("%s{RESET}" % SEP)
            else:
                if tokens[i + 1].bg:
                    prompt.append("{BACKGROUND_%s}" % tokens[i + 1].bg)
                if sec.bg:
                    prompt.append("{%s}" % sec.bg)
                prompt.append(SEP)
    return "".join(prompt)


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
