from typing import Dict

from django.contrib.auth.models import User

from notes.doa import notebooks, notes
from notes.models import UserProfile
from notes.syntax_highlighting import syntax_highlighting_stylesheet_link
from notes.themes import stylesheet_url


def styled_context(user: User) -> Dict:
    # Default themes for non-logged in users
    if not user.is_authenticated:
        return {
            'compact_mode': 'Off',
            'stylesheet': stylesheet_url(''),
            'syntax_highlighting_stylesheet': syntax_highlighting_stylesheet_link(''),
        }

    # User-specific themes
    profile = UserProfile.objects.filter(user=user).get()
    theme = profile.theme
    syntax_highlighting_style = profile.syntax_highlighting_style
    compact_mode = profile.compact_mode

    return {
        'compact_mode': compact_mode,
        'stylesheet': stylesheet_url(theme),
        'syntax_highlighting_stylesheet': syntax_highlighting_stylesheet_link(syntax_highlighting_style),
    }


def regular_context(user: User) -> Dict:
    context = styled_context(user)

    if user.is_authenticated:
        context['notebooks'] = notebooks(user)
        context['notes'] = notes(user)
    return context
