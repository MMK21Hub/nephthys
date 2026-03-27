from jinja2 import Environment
from jinja2 import Template

from nephthys.utils.env import env

jinja_env = Environment()
jinja_env.globals = {"app_title": env.app_title}


def template(string: str) -> Template:
    """Create a Jinja template from a string, for use in transcripts"""
    return jinja_env.from_string(string)
