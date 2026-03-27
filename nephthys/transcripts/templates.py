from jinja2 import Environment
from jinja2 import Template


jinja_env = Environment()


def template(string: str) -> Template:
    """Create a Jinja template from a string, for use in transcripts"""
    return jinja_env.from_string(string)
