import functools
import os
import re
import typing as tp
from pathlib import Path

import xonsh.tools as xt
from xonsh.built_ins import XSH
from .colors import Colors, get_contrast_color

env = XSH.env
XSH_FIELDS = env["PROMPT_FIELDS"]
XSH_FIELDS["time_format"] = "%I:%M:%S%p"


class RichField(tp.NamedTuple):
    value: str
    fg: str
    sep: "str|None" = None


def add_pl_field(fn):
    """a decorator that add function wrappers for $PROMPT_FIELDS `fn` and `fn__pl_colors`"""
    fld_name = fn.__name__

    @functools.wraps(fn)
    def wrapped():
        result = fn()
        # if it is tuple then it contains color info as well
        if isinstance(result, RichField):
            value = result.value
            add_pl_colors(fld_name, result.fg)
            if result.sep:
                add_pl_sep(fld_name, result.sep)
        else:
            value = result
        return value

    XSH_FIELDS[fld_name] = wrapped
    return wrapped


def add_field(fn):
    XSH_FIELDS[fn.__name__] = fn
    return fn


def add_pl_colors(name: str, bg: str, color: "str|None" = None):
    """for the prompt field set the background and foreground color"""
    if bg:
        color = color or get_contrast_color(bg.lstrip("#"))
        colors = (color, bg)
    else:
        colors = ("", "")  # no need to add colors. eg. prompt_end
    XSH_FIELDS[f"{name}__pl_colors"] = colors


def add_pl_sep(name: str, sep: str):
    """for the prompt field thin separator"""
    XSH_FIELDS[f"{name}__pl_sep"] = sep


def set__pl_defaults():
    """add colors/sep for the default prompt-fields"""
    for defs in [
        ("user", Colors.SAND),
        ("hostname", Colors.BLUE),
        ("localtime", Colors.SAND),
        ("env_name", Colors.EMERALD),
        ("current_job", Colors.ROSE),
        ("prompt_end", ""),
        ("cwd", Colors.CYAN),
        ("env_name", Colors.EMERALD),
        ("full_env_name", Colors.EMERALD),
    ]:
        add_pl_colors(*defs)

    for fld, sep in [
        ("cwd", os.sep),
    ]:
        add_pl_sep(fld, sep)


@functools.lru_cache
def poetry_env_naming():
    # if using poetry's venv naming scheme like <venv-name>-<hash>-py<ver>
    return re.compile(r"(?P<name>\S+)-\w+-py(?P<version>[\d.]+)")


@add_pl_field
def full_env_name():
    """When the `env_name` is
    - `.venv` show the name of the parent folder
    - contains `-py3.*` (when it is poetry created) shows the project name part alone
    """
    env_name: str = XSH_FIELDS["env_name"]()
    if not env_name:
        return

    venv_path = Path(env.get("VIRTUAL_ENV"))
    if venv_path.name == ".venv":
        env_name = venv_path.parent.name

    sep = "\0"
    if match := poetry_env_naming().match(venv_path.name):
        name, version = match.groups()
        env_name = sep.join([name, version])

    return RichField(env_name, Colors.EMERALD, sep)


def _background_jobs():
    num = len([task for task in XSH.all_jobs.values() if task.get("bg")])
    if num:
        return f"💼{num}"


@add_pl_field
def background_jobs():
    """Show number of background jobs"""
    jobs = _background_jobs()
    if jobs:
        return RichField(_background_jobs(), Colors.SERENE)


def deep_get(dictionary, *keys) -> tp.Optional[tp.Any]:
    """
    >>> deep_get({"1": {"10": {"100": 200}}}, "1", "10", "100")
    200
    """
    dic = dictionary
    for ky in keys:
        if dic is None:
            return None
        dic = dic.get(ky)
    return dic


# @add_pl_field
# def py_pkg_info():
#     """Show package name and version if current directory has setup.py or pyproject.toml"""
#     py_logo = "\ue73c"  #  - python logo font
#     import tomlkit
#
#     # todo
#     proj = tomlkit.parse(proj_file.read_text())
#
#     proj_name = deep_get(proj, "tool", "poetry", "name")
#     proj_version = deep_get(proj, "tool", "poetry", "version")
#
#     return f"{py_logo} {proj_name}-{proj_version}"
#
#
# @add_pl_field
# def os_icon():
#     """Show logo from nerd-fonts for current distro"""
#
#     # todo
#     return None


@add_pl_field
def user_at_host():
    val = XSH_FIELDS["user"] + "✸" + XSH_FIELDS["hostname"]
    return RichField(val, Colors.VIOLET)


@add_pl_field
def ret_code():
    if XSH.history.rtns:
        return_code = XSH.history.rtns[-1]
        if return_code != 0:
            return RichField(f"[{return_code}]", Colors.RED)


@add_field
def prompt_end():
    """prompt end symbol with color red if last job failed"""
    prompt = "#" if xt.is_superuser() else "❯"
    color = Colors.WHITE
    if XSH.history and XSH.history.rtns:
        return_code = XSH.history.rtns[-1]
        if return_code != 0:
            color = Colors.RED
    return "{%s}%s{RESET} " % (color, prompt)


@add_pl_field
def gitstatus():
    """powerline version of gitstatus prompt-field from Xonsh"""
    from xonsh.prompt.gitstatus import get_gitstatus_fields, _DEFS, _is_hidden, _get_def

    fields = get_gitstatus_fields()
    if fields is None:
        return None

    def get_def(attr) -> str:
        symbol = _get_def(attr) or ""
        if "}" in symbol:  # strip color
            symbol = symbol.split("}")[1]
        return symbol

    def gather_group(*flds):
        for fld in flds:
            if not _is_hidden(fld):
                val = fields[fld]
                if not val:
                    continue
                yield get_def(fld) + str(val)

    def get_parts():
        for grp in (
            (_DEFS.BRANCH,),
            (_DEFS.OPERATION,),
            (_DEFS.AHEAD, _DEFS.BEHIND),
            (_DEFS.STAGED, _DEFS.CONFLICTS),
            (_DEFS.CHANGED, _DEFS.DELETED),
            (_DEFS.UNTRACKED, _DEFS.STASHED),
            (_DEFS.LINES_ADDED, _DEFS.LINES_REMOVED),
        ):  # each group appears inside a separator
            val = "".join(gather_group(*grp))
            if val:
                yield val

    def get_color():
        if fields[_DEFS.CONFLICTS]:
            return Colors.ORANGE
        if any(
            map(lambda x: fields[x], [_DEFS.CHANGED, _DEFS.DELETED, _DEFS.UNTRACKED])
        ):
            return Colors.PINK

        return Colors.GREEN  # clean

    sep = "\0"
    return RichField(sep.join(get_parts()), get_color(), sep)
