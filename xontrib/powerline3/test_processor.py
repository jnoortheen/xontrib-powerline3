from xonsh.prompt.base import _ParsedToken

from user_xsh.prompt.processor import split_by_lines, Section


def test_prompt_lines():
    tokens = [_ParsedToken(value='', field='vte_new_tab_cwd'),
              _ParsedToken(value='{cwd}', field='cwd'),
              _ParsedToken(value='\ue0a0{gitstatus}', field='gitstatus'),
              _ParsedToken(value='{ret_code}', field='ret_code'),
              _ParsedToken(value='\n', field=None),
              _ParsedToken(value='', field='full_env_name'),
              _ParsedToken(value='❯ ', field=None), ]

    assert list(split_by_lines(tokens)) == [
        [Section(line='{cwd}', fg='WHITE', bg='CYAN'),
         Section(line='\ue0a0{gitstatus}', fg='WHITE', bg='BLACK'),
         Section(line='{ret_code}', fg='WHITE', bg='RED')],
        [Section(line='❯ ', fg='WHITE', bg='BLACK')]
    ]
