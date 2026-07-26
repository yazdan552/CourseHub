from django import forms
from .models import Course
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = [
            "title",
            "instructor",
            "description",
            "price",
        ]





class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "password1",
            "password2",
        )