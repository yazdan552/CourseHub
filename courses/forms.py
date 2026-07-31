from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Course, Instructor , Category


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
            'categories': forms.SelectMultiple(attrs={
                'class': 'form-select',
                'size': 5,  # نمایش ۵ آیتم
            }),
        }

    def clean_categories(self):
        """
        اطمینان از اینکه حداقل یک دسته‌بندی انتخاب شده است
        """
        categories = self.cleaned_data.get('categories')
        if not categories:
            raise forms.ValidationError(
                "Please select at least one category."
            )
        return categories


class RegisterForm(UserCreationForm):
    class Meta:
        model = User

        fields = (
            "username",
            "email",
            "password1",
            "password2",
        )


class InstructorProfileForm(forms.ModelForm):
    """
    فرم ویرایش پروفایل مدرس
    فقط فیلدهای phone و bio قابل ویرایش هستند
    """

    class Meta:
        model = Instructor
        fields = ['phone', 'bio']

        widgets = {
            'bio': forms.Textarea(attrs={
                'rows': 5,
                'class': 'form-control',
                'placeholder': 'Tell us about yourself...'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., +98 912 123 4567'
            }),
        }

        labels = {
            'phone': 'Phone Number',
            'bio': 'Biography',
        }
