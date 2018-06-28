from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm

from notes.models import UserProfile
from notes.user_profiles import regular_context


@login_required
def logout_view(request):
    logout(request)
    return redirect('home')


def register_view(request):
    if request.method != 'POST':
        form = UserCreationForm()
    else:
        form = UserCreationForm(data=request.POST)

        if form.is_valid():
            new_user = form.save()
            UserProfile.objects.create(user=new_user)
            authed_user = authenticate(username=new_user.username, password=request.POST['password1'])
            login(request, authed_user)
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

        if form.is_valid():
            data = form.clean()
            authed_user = authenticate(username=data['username'], password=data['password'])

            # Create user profile if one does not exist (for users made through createsuperuser)
            if not UserProfile.objects.filter(user=authed_user).exists():
                UserProfile.objects.create(user=authed_user)

            login(request, authed_user)
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

        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect('home')

    # Render
    context = regular_context(request.user)
    context['form'] = form
    return render(request, 'change_password.html', context)
