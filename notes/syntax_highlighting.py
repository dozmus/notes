STYLE_SHEETS = [
    'default',
    'autumn',
    'borland',
    'bw',
    'colorful',
    'emacs',
    'friendly',
    'fruity',
    'manni',
    'monokai',
    'murphy',
    'murphy',
    'native',
    'pastie',
    'perldoc',
    'tango',
    'trac',
    'vim',
    'vs',
]

SYNTAX_HIGHLIGHTING_CHOICES = tuple([(x, x) for x in STYLE_SHEETS])


def stylesheet_link(syntax_highlighting_style):
    for stylesheet in STYLE_SHEETS:
        if syntax_highlighting_style == stylesheet:
            return 'css/pygments/%s.css' % stylesheet
    raise RuntimeError
