import re
from unicodedata import normalize

from jinja2.ext import Extension


SLUG_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_"

def slug(text: str, separator: str = "_", permitted_chars: str = SLUG_CHARS):
    """Generate a slug for the `text`.

    >>> slug(' ÁLVARO  justen% ')
    'alvaro_justen'
    >>> slug(' ÁLVARO  justen% ', separator='-')
    'alvaro-justen'
    """

    # Strip non-ASCII characters
    # Example: u' ÁLVARO  justen% ' -> ' ALVARO  justen% '
    text = normalize("NFKD", text.strip()).encode("ascii", "ignore").decode("ascii")

    # Replace word boundaries with separator
    text = re.sub("(\\w\\b)", "\\1" + re.escape(separator), text)

    # Remove non-permitted characters and put everything to lowercase
    # Example: u'_ALVARO__justen%_' -> u'_alvaro__justen_'
    allowed_chars = list(permitted_chars) + [separator]
    text = "".join(char for char in text if char in allowed_chars).lower()

    # Remove double occurrencies of separator
    # Example: u'_alvaro__justen_' -> u'_alvaro_justen_'
    text = re.sub("(_+)" if separator == "_" else "(" + re.escape(separator) + "+)", separator, text)

    # Strip separators
    # Example: u'_alvaro_justen_' -> u'alvaro_justen'
    return text.strip(separator)


class CustomFilters(Extension):
    def __init__(self, env):
        self.env = env
        self.env.filters["slug"] = slug
