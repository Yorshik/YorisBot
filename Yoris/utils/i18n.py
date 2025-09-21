class SafeDict(dict):
    def __missing__(self, key):
        return f"{key}?"


def translate(text: str, ctx=None, **kwargs):
    return text.format_map(SafeDict(**kwargs))
