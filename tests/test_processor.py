from xonsh.prompt.base import _ParsedToken, ParsedTokens, PromptFormatter

import pytest


@pytest.fixture(scope="module", autouse=True)
def xsh():
    from xonsh.built_ins import XSH

    XSH.load()
    from xontrib.powerline3 import main

    main()
    yield XSH
    XSH.unload()


@pytest.fixture
def prompt(xsh, tmpdir):
    from xonsh.dirstack import with_pushd

    prompt = "{env_name}{user_at_host}{cwd}\n{gitstatus}{prompt_end} "
    xsh.env["PROMPT"] = prompt
    xsh.env["POWERLINE_MODE"] = "powerline"

    formatter = PromptFormatter()
    fields = xsh.env["PROMPT_FIELDS"]
    fields.update(
        dict(
            env_name="venv1",
            user="user1",
            hostname="bot",
            gitstatus="gitstatus",
            cwd="/home/tst",
        )
    )
    with with_pushd(str(tmpdir)):
        yield formatter(prompt)


def test_prompt_lines(prompt, tmpdir):
    exp_first = (
        "{BACKGROUND_#009B77}{INTENSE_WHITE}venv1"
        "{BACKGROUND_#6B5B95}{#009B77}"
        "{INTENSE_WHITE}user1✸bot"
        "{BACKGROUND_#181818}{#6B5B95}"
        "{WHITE}/home/tst"
        "{RESET}{#181818}{RESET}"
    )
    exp_sec = (
        "{BACKGROUND_#181818}{WHITE}gitstatus{#181818}\ue0b0{INTENSE_WHITE}❯\ue0b0 "
        "{RESET}\ue0b0{RESET}"
    )
    first_line, sec_line = prompt.splitlines(keepends=False)
    from xonsh.tools import print_color

    print_color(first_line)
    print_color(sec_line)
    assert first_line == exp_first
    assert sec_line == exp_sec
