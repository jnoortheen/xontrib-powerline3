import typing as tp
import builtins
import xonsh.built_ins as xb
from pathlib import Path

XSH = tp.cast(xb.XonshSession, builtins.__xonsh__)
XSH_ENV = XSH.env
XSH_FIELDS = XSH_ENV["PROMPT_FIELDS"]
XSH_FIELDS["time_format"] = "%I:%M:%S%p"


def add_as_field(f):
    XSH_FIELDS[f.__name__] = f


@add_as_field
def full_env_name():
    """When the `env_name` is
      - `.venv` show the name of the parent folder
      - contains `-py3.*` (when it is poetry created) shows the project name part alone

    Returns
    -------
    str
        python env_name
    """
    env_name: str = XSH_FIELDS["env_name"]()
    if env_name:
        venv_path = Path(XSH_ENV.get("VIRTUAL_ENV"))
        if venv_path.name == ".venv":
            return venv_path.parent.name
        if "-py" in env_name:
            name = venv_path.name.rsplit("-", 2)[0]
            return name

    return env_name


@add_as_field
def background_jobs():
    """Show number of background jobs"""
    num = 0
    for task in XSH.all_jobs.values():
        if task.get("bg"):
            num += 1

    return f"💼{num}" if num else None


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


@add_as_field
def py_pkg_info():
    """Show package name and version if current directory has setup.py or pyproject.toml"""
    py_logo = "\ue73c"  #  - python logo font
    import tomlkit

    # todo
    proj = tomlkit.parse(proj_file.read_text())

    proj_name = deep_get(proj, "tool", "poetry", "name")
    proj_version = deep_get(proj, "tool", "poetry", "version")

    return f"{py_logo} {proj_name}-{proj_version}"


@add_as_field
def os_icon():
    """Show logo from nerd-fonts for current distro"""
    import distro

    # todo
    return None


@add_as_field
def user_at_host():
    return XSH_FIELDS["user"] + "✸" + XSH_FIELDS["hostname"]


@add_as_field
def gitstatus_pl():
    """gitstatus prompt with powerline separtors"""
    from xonsh.prompt.gitstatus import get_gitstatus_fields, _DEFS, _is_hidden, _get_def
    from xontrib_powerline3.processor import POWERLINE_SYMBOLS

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

    groups = (
        (_DEFS.BRANCH, _DEFS.AHEAD, _DEFS.BEHIND, _DEFS.OPERATION),
        (_DEFS.STAGED, _DEFS.CONFLICTS),
        (_DEFS.CHANGED, _DEFS.DELETED),
        (_DEFS.UNTRACKED, _DEFS.STASHED),
        (_DEFS.LINES_ADDED, _DEFS.LINES_REMOVED),
    )
    parts = ("".join(gather_group(*grp)) for grp in groups)

    _, THIN, _, _ = POWERLINE_SYMBOLS
    return THIN.join((p for p in parts if p))
