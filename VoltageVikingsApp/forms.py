from captcha.fields import CaptchaField
from allauth.account.forms import LoginForm, SignupForm
from django import forms
from .models import UserProfile
from django.core.exceptions import ValidationError


class CaptchaLoginForm(LoginForm):
    captcha = CaptchaField()


class CapthaSignUpForm():
    captcha = CaptchaField()


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        exclude = ['lat', 'lon', 'available', 'got_loc', 'completed_profile', 'user']

        def clean_phone_number(self):
            phone_number = self.cleaned_data['phone_number']
            if not phone_number:
                return phone_number  # Allow empty phone numbers
            if len(phone_number) < 10:
                raise ValidationError("Phone number must be  atleast 10 digits")
            if not phone_number.isdigit():
                raise ValidationError("Phone number must only contain digits")
            return phone_number
