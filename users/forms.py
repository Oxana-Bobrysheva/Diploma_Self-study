# users/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        label="Email",
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "Введите ваш email"}
        ),
    )
    name = forms.CharField(
        required=True,
        label="Имя",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Введите ваше имя"}
        ),
    )
    role = forms.ChoiceField(
        choices=User.ROLE_CHOICES,
        initial="student",
        label="Роль",
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    class Meta:
        model = User
        fields = ["name", "email", "role", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to password fields
        self.fields["password1"].widget.attrs.update({"class": "form-control"})
        self.fields["password2"].widget.attrs.update({"class": "form-control"})

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = user.email  # Set username to email
        if commit:
            user.save()
        return user


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["name", "phone", "city", "avatar"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "city": forms.TextInput(attrs={"class": "form-control"}),
            "avatar": forms.FileInput(attrs={"class": "form-control"}),
        }
        labels = {
            "name": "Имя",
            "phone": "Телефон",
            "city": "Город",
            "avatar": "Аватар",
        }
