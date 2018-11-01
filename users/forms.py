from django.contrib.auth import forms, login, authenticate, update_session_auth_hash

from notes.models import UserProfile


class UserCreationForm(forms.UserChangeForm):
    def create(self, request):
        if self.is_valid():
            new_user = self.save()
            UserProfile.objects.create(user=new_user)
            authed_user = authenticate(username=new_user.username, password=request.POST['password1'])
            login(request, authed_user)
            return True
        return False


class AuthenticationForm(forms.AuthenticationForm):
    def login(self, request):
        if self.is_valid():
            username = self.cleaned_data['username']
            password = self.cleaned_data['password']
            authed_user = authenticate(username=username, password=password)

            # Create user profile if one does not exist (for users created through createsuperuser)
            if not UserProfile.objects.filter(user=authed_user).exists():
                UserProfile.objects.create(user=authed_user)

            login(request, authed_user)
            return True
        return False


class PasswordChangeForm(forms.PasswordChangeForm):
    def update(self, request):
        if self.is_valid():
            user = self.save()
            update_session_auth_hash(request, user)
            return True
        return False
