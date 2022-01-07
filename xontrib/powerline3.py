from xonsh.built_ins import XSH
import xontrib_powerline3.processor as xpp
import xontrib_powerline3.fields as xpf

# load defaults
def main():
    xpf.add_default_prompt_colors()
    XSH.env["PROMPT_TOKENS_FORMATTER"] = xpp.process_prompt_tokens


main()
