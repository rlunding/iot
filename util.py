import socket
import re
from sphinx.util import docstrings

def get_free_port() -> int:
    s = socket.socket()
    s.bind(('', 0))
    p = s.getsockname()[1]
    s.close()
    return p


PARAM_OR_RETURNS_REGEX = re.compile(":(?:param|returns)")
RETURNS_REGEX = re.compile(":returns: (?P<doc>.*)", re.S)
PARAM_REGEX = re.compile(":param (?P<name>[\*\w]+): (?P<doc>.*?)"
                         "(?:(?=:param)|(?=:return)|(?=:raises)|\Z)", re.S)


def reindent(string):
    return "\n".join(l.strip() for l in string.strip().split("\n"))


def parse_docstring(docstring):
    """Parse the docstring into its components.
    :returns: a dictionary of form
              {
                  "short_description": ...,
                  "long_description": ...,
                  "params": [{"name": ..., "doc": ...}, ...],
                  "returns": ...
              }
    """

    short_description = long_description = returns = ""
    params = []

    if docstring:
        docstring = "\n".join(docstrings.prepare_docstring(docstring))

        lines = docstring.split("\n", 1)
        short_description = lines[0]

        if len(lines) > 1:
            long_description = lines[1].strip()

            params_returns_desc = None

            match = PARAM_OR_RETURNS_REGEX.search(long_description)
            if match:
                long_desc_end = match.start()
                params_returns_desc = long_description[long_desc_end:].strip()
                long_description = long_description[:long_desc_end].rstrip()

            if params_returns_desc:
                params = [
                    {"name": name,
                     "doc": "\n".join(docstrings.prepare_docstring(doc))}
                    for name, doc in PARAM_REGEX.findall(params_returns_desc)
                ]

                match = RETURNS_REGEX.search(params_returns_desc)
                if match:
                    returns = reindent(match.group("doc"))

    return {
        "short_description": short_description,
        "long_description": long_description,
        "params": params,
        "returns": returns
    }
