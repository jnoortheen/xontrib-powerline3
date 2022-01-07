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
def format_prompt(xsh, tmpdir):
    def factory(prompt: str):
        xsh.env["PROMPT"] = prompt
        xsh.env["POWERLINE_MODE"] = "powerline"

        formatter = PromptFormatter()
        fields = xsh.env["PROMPT_FIELDS"]
        fields.update(
            dict(
                env_name="venv1",  # fg=INTENSE_WHITE, bg=009B77
                user="user1",
                hostname="bot",
                gitstatus="gitstatus",
                cwd="/home/tst",
            )
        )
        return formatter(prompt)

    return factory


def test_left_prompt_process_ansi_pre_post(format_prompt):
    # tok.field=None fg='' bg=''
    # tok.field='env_name' fg='INTENSE_WHITE' bg='#009B77'
    # tok.field='user_at_host' fg='INTENSE_WHITE' bg='#6B5B95'
    # tok.field='cwd' fg='white' bg='#181818'
    exp_first = (
        "\x01\x1b]133;A\x07\x02"
        "{BACKGROUND_#009B77}{INTENSE_WHITE}venv1"
        "{BACKGROUND_#6B5B95}{#009B77}"
        "{INTENSE_WHITE}user1✸bot"
        "{BACKGROUND_#181818}{#6B5B95}"
        "{WHITE}/home/tst"
        "{RESET}{#181818}{RESET}"
    )
    exp_sec = (
        "{BACKGROUND_#181818}{WHITE}gitstatus"
        "{RESET}{#181818}{RESET}"
        "{INTENSE_WHITE}❯ "
        "\x01\x1b]133;B\x07\x02"
    )
    template = (
        "\x01\x1b]133;A\x07\x02"  # empty prefix
        "{env_name}{user_at_host}{cwd}\n{gitstatus}{prompt_end}"
        "\x01\x1b]133;B\x07\x02"  # empty suffix
    )
    prompt = format_prompt(template)
    first_line, sec_line = prompt.splitlines(keepends=False)

    # for debugging
    from xonsh.tools import print_color

    print_color(first_line)
    print_color(sec_line)
    assert first_line == exp_first
    assert sec_line == exp_sec


def test_left_prompt_process_normal(format_prompt):
    """all parts have a field associated"""
    exp_first = (
        "{BACKGROUND_#009B77}{INTENSE_WHITE}venv1"
        "{BACKGROUND_#6B5B95}{#009B77}"
        "{INTENSE_WHITE}user1✸bot"
        "{BACKGROUND_#181818}{#6B5B95}"
        "{WHITE}/home/tst"
        "{RESET}{#181818}{RESET}"
    )
    exp_sec = (
        "{BACKGROUND_#181818}{WHITE}gitstatus"
        "{RESET}{#181818}{RESET}"
        "{INTENSE_WHITE}❯ "
    )
    template = "{env_name}{user_at_host}{cwd}\n{gitstatus}{prompt_end}"
    prompt = format_prompt(template)
    first_line, sec_line = prompt.splitlines(keepends=False)

    # for debugging
    from xonsh.tools import print_color

    print_color(first_line)
    print_color(sec_line)
    assert first_line == exp_first
    assert sec_line == exp_sec
