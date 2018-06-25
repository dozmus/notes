THEME_STYLESHEETS = [
    'light',
    'dark',
]

THEME_CHOICES = tuple([(x, x) for x in THEME_STYLESHEETS])


def stylesheet_url(syntax_highlighting_style, default=THEME_STYLESHEETS[0]):
    for stylesheet in THEME_STYLESHEETS:
        if syntax_highlighting_style == stylesheet:
            return 'css/%s.css' % stylesheet
    return 'css/%s.css' % default


def stylesheet_ie_url(syntax_highlighting_style, default=THEME_STYLESHEETS[0]):
    for stylesheet in THEME_STYLESHEETS:
        if syntax_highlighting_style == stylesheet:
            return 'css/%s-ie.css' % stylesheet
    return 'css/%s-ie.css' % default
