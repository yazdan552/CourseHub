from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Course


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course

        exclude = [
            "instructor",
            "created_at",
        ]

        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class RegisterForm(UserCreationForm):
    class Meta:
        model = User

        fields = (
            "username",
            "email",
            "password1",
            "password2",
        )