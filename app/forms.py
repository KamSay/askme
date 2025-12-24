from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
import os
import time


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()

        username = cleaned_data.get("username")
        password = cleaned_data.get("password")

        if username is None or password is None:
            return cleaned_data

        user = authenticate(
            request=self.request,
            username=username,
            password=password,
        )

        if user is None:
            raise forms.ValidationError("Неверный логин или пароль")

        if not user.is_active:
            raise forms.ValidationError("Пользователь отключён")

        cleaned_data["user"] = user
        return cleaned_data



class RegistrationForm(forms.Form):
    username = forms.CharField()
    email = forms.EmailField()
    password = forms.CharField()
    password_repeat = forms.CharField()
    avatar = forms.ImageField(required=False)

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if not avatar:
            return avatar

        ext = os.path.splitext(avatar.name)[1]
        avatar.name = f"{int(time.time())}{ext}"
        return avatar

    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get("password")
        password_repeat = cleaned_data.get("password_repeat")
        email = cleaned_data.get("email")
        username = cleaned_data.get("username")

        if password and password_repeat and password != password_repeat:
            raise forms.ValidationError("Passwords do not match")

        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email address is already registered")

        if username and User.objects.filter(username=username).exists():
            raise forms.ValidationError("This login is already taken")

        return cleaned_data


class AskForm(forms.Form):
    title = forms.CharField()
    text = forms.CharField()
    tags = forms.CharField()

    def clean(self):
        cleaned_data = super().clean()

        tags = cleaned_data.get('tags')
        if tags:
            cleaned_data['tags'] = [t.strip() for t in tags.split(";") if t.strip()]
        return cleaned_data


class AnswerForm(forms.Form):
    text = forms.CharField(required=True)

    def clean(self):
        cleaned_data = super().clean()
        text = cleaned_data.get('text')
        if not text:
            raise forms.ValidationError("Answer is empty")
        return cleaned_data


class SettingsForm(forms.Form):
    username = forms.CharField()
    email = forms.CharField()
    avatar = forms.ImageField(required=False)

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if not avatar:
            return avatar

        ext = os.path.splitext(avatar.name)[1]
        avatar.name = f"{int(time.time())}{ext}"
        return avatar

    def clean(self):
        cleaned_data = super().clean()

        username = cleaned_data.get('username')
        email = cleaned_data.get('email')

        if username != self.user.username and User.objects.filter(username=username).exists():
            raise forms.ValidationError("This login is already taken")

        if email != self.user.email and User.objects.filter(email=email).exists() and self.check_email():
            raise forms.ValidationError("This email is already taken")

        return cleaned_data

    def check_email(self):
        return True