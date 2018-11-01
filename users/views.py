from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import logout

from notes.user_profiles import regular_context
from users.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm


@login_required
def logout_view(request):
    logout(request)
    return redirect('home')


def register_view(request):
    if request.method != 'POST':
        form = UserCreationForm()
    else:
        form = UserCreationForm(data=request.POST)

        if form.create(request):
            return redirect('home')

    # Render
    context = regular_context(request.user)
    context['form'] = form
    return render(request, 'register.html', context)


def login_view(request):
    if request.method != 'POST':
        form = AuthenticationForm()
    else:
        form = AuthenticationForm(data=request.POST)

        if form.login(request):
            return redirect('home')

    # Render
    context = regular_context(request.user)
    context['form'] = form
    return render(request, 'login.html', context)


@login_required
def change_password(request):
    # Source: https://simpleisbetterthancomplex.com/tips/2016/08/04/django-tip-9-password-change-form.html
    if request.method != 'POST':
        form = PasswordChangeForm(request.user)
    else:
        form = PasswordChangeForm(request.user, request.POST)

        if form.update(request):
            return redirect('home')

    # Render
    context = regular_context(request.user)
    context['form'] = form
    return render(request, 'change_password.html', context)
