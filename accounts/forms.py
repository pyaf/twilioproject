from django import forms
from django.conf import settings
from django.utils.translation import ugettext as _
from django.contrib.auth.password_validation import validate_password

from .models import User, now_plus_48_hours


class RegisterForm(forms.ModelForm):
    phone_number = forms.IntegerField(required=True)
    password1 = forms.CharField(widget=forms.PasswordInput())
    password2 = forms.CharField(widget=forms.PasswordInput())
    MIN_LENGTH = 4

    class Meta:
        model = User
        fields = ['username','phone_number', 'password1', 'password2',
                  'full_name']

    def clean_username(self):
        username = self.data.get('username')
        return username

    def clean_password1(self):
        password = self.data.get('password1')
        validate_password(password)
        if password != self.data.get('password2'):
            raise forms.ValidationError(_("Passwords do not match"))
        return password

    def clean_phone_number(self):
        phone_number = self.data.get('phone_number')
        print(User.objects.filter(phone_number=phone_number))
        if User.objects.filter(phone_number=phone_number).exists():
            raise forms.ValidationError(
                _("Another user with this phone number already exists"))
        return phone_number

    def save(self, *args, **kwargs):
        user = super(RegisterForm, self).save(*args, **kwargs)
        user.set_password(self.cleaned_data['password1'])
        print('Saving user')
        user.save()
        return user

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField()

    class Meta:
        fields = ['username','password']
