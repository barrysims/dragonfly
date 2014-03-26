"""Some useful commands for navigating, selecting, and editing the current line of text"""

import re

from itertools import islice
from dragonfly import Text, Key, Function, Dictation, Choice, Mimic, Clipboard, Grammar, IntegerRef

from utils.series_mapping_rule import SeriesMappingRule
from utils.clipboard import text_clip, save_clip, reverse_clip, restore_clip
from utils.tokens import alphabet, symbol, tokens


def switch_task(n=0):
    """Switches between applications in the taskbar"""
    Key("w-" + str(n)).execute()


def nth(iterable, n, default=None):
    """Returns the nth item or a default value"""
    return next(islice(iterable, n-1, None), default)


def delete_forward(n=0):
    """Deletes from the carat to the next space character"""
    select_forward(" ", "", n)
    Key("delete").execute()


def delete_backward(n=0):
    """Deletes backwards from the carat to the previous space character"""
    select_backward(" ", "", n)
    Key("delete").execute()


def jump_forward(text="", token="", n=0):
    """Moves the carat to the next instance of the token"""
    distance = _locate_forward(text, token, n)
    Key("right:" + str(distance)).execute()
    return distance


def jump_backward(text="", token="", n=0):
    """Moves the carat back to the previous instance of the token"""
    distance = _locate_backward(text, token, n)
    Key("left:" + str(distance)).execute()
    return distance


def select_forward(text="", token="", n=0):
    """Selects forwards to the next instance of the token"""
    distance = _locate_forward(text, token, n)
    Key("s-right:" + str(distance)).execute()


def select_backward(text="", token="", n=0):
    """Selects backwards to the previous instance of the token"""
    distance = _locate_backward(text, token, n)
    Key("s-left:" + str(distance)).execute()


def select_next(text=""):
    """Selects forwards to the next instance of the previously selected token"""
    save_clip()
    Key("c-c/5").execute()
    clip_contents = text_clip()
    n = len(re.findall(previous_token, clip_contents))
    select_forward(text, previous_token, n + 1)
    restore_clip()


def _locate_forward(text="", token="", n=0):
    """Returns the number of characters from the carat to the next instance of the token"""
    return _locate(
        _copy_forward,
        text,
        token,
        n
    )


def _locate_backward(text="", token="", n=0):
    """Returns the number of characters from the carat to the previous instance of the token"""
    return _locate(
        _copy_backward,
        text,
        token,
        n
    )


def _locate(copy, text="", token="", n=0):
    """Calculates the number of characters to the next or previous instance of the token"""
    global previous_token
    pattern = previous_token
    if str(text) != "":
        pattern = str(text)
    elif token != "":
        pattern = token
    previous_token = pattern
    copy()
    clip_contents = text_clip()
    matches = re.compile(pattern).finditer(str(clip_contents)[1:])
    restore_clip()
    return nth(matches, n).start() + 2


def _copy_backward():
    """Copies from the carat to the start of the current line of text"""
    _copy_chunk("s-home", "right")
    reverse_clip()


def _copy_forward():
    """Copies from the carat to the end of the current line of text"""
    _copy_chunk("s-end", "left")


def _copy_chunk(to, direction):
    """Copies a section of the current line to the clipboard"""
    save_clip()
    Key(to + ", c-c/5").execute()
    Key(direction).execute()


def just(text=""):
    """Prints a word without calling any functions associated with that word"""
    Text(re.sub(r'[\W]', '', str(text))).execute()


series_rule = SeriesMappingRule(
    mapping={

        "word <text>": Function(just),

        "drop word": Mimic("delete previous word"),
        "kill word": Mimic("delete next word"),

        "skip [<n>]": Function(jump_forward, text=""),
        "skip <token>": Function(jump_forward),
        "step [<n>]": Function(jump_backward, text=""),
        "step <token>": Function(jump_backward),

        "drop [<n>]": Function(delete_backward),
        "ditch [<n>]": Function(delete_forward),
        "select [<n>]": Function(select_forward, text=""),
        "select next": Function(select_next, text=""),
        "select <token>": Function(select_forward),

        "trunk": Key("s-end, delete"),
        "chop": Key("s-home, delete"),

        # Belongs in a different module
        "prog [<n>]": Function(switch_task),
    },
    extras=[
        IntegerRef("n", 1, 1000),
        IntegerRef("n2", 1, 1000),
        IntegerRef("n3", 1, 1000),
        Dictation("text"),
        Choice("symbol", symbol),
        Choice("alphabet", alphabet),
        Choice("token", tokens),
    ],
    defaults={
        "n": 1
    }
)

clipboard = Clipboard()
previous_token = ""

global_context = None  # Context is None, so grammar will be globally active.
grammar = Grammar("line editing", context=global_context)
grammar.add_rule(series_rule)
grammar.load()

# Unload function which will be called at unload time.
def unload():
    global grammar
    if grammar:
        grammar.unload()
    grammar = None
