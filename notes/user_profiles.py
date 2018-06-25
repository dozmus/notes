from typing import Dict

from django.contrib.auth.models import User

from notes.doa import notebooks, notes
from notes.models import UserProfile
from notes.syntax_highlighting import syntax_highlighting_stylesheet_link
from notes.themes import stylesheet_url, stylesheet_ie_url


def styled_context(user: User) -> Dict:
    if not user.is_authenticated:
        return {
            'stylesheet': stylesheet_url(''),
            'stylesheet_ie': stylesheet_ie_url(''),
            'syntax_highlighting_stylesheet': syntax_highlighting_stylesheet_link(''),
        }

    profile = UserProfile.objects.filter(user=user).get()
    theme = profile.theme
    syntax_hightlighting_style = profile.syntax_highlighting_style

    return {
        'stylesheet': stylesheet_url(theme),
        'stylesheet_ie': stylesheet_ie_url(theme),
        'syntax_highlighting_stylesheet': syntax_highlighting_stylesheet_link(syntax_hightlighting_style),
    }


def regular_context(user: User) -> Dict:
    context = styled_context(user)
    context['notebooks'] = notebooks(user)
    context['notes'] = notes(user)
    return context
