from django import forms
from django.core.validators import RegexValidator
from django.contrib.auth.forms import (AuthenticationForm, UserCreationForm,
                                       UserChangeForm)
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
from django.shortcuts import get_object_or_404

from .models import Profile, City

import re


class ProfileForm(forms.ModelForm):
    """Form describing additonal user details 
    """
    date_of_birth = forms.DateField(
        input_formats=('%Y-%m-%d', '%m/%d/%Y', '%m/%d/%y',)
    )

    class Meta:
        model = Profile
        fields = [
            'date_of_birth',
            'bio',
            'cats_or_dogs',
            'favourite_colour',
            'hobby',
            'country',
            'city',
        ]

    def __init__(self, *args, **kwargs):
        """Changing init to clear out Cities options in select field so 
        we can first get Country selection and then re-populate Cities 
        based on the selected Country
        """
        super().__init__(*args, **kwargs)
        self.fields['city'].queryset = City.objects.none()

        if 'country' in self.data:
            try:
                country_id = int(self.data.get('country'))
                self.fields['city'].queryset = City.objects.filter(
                    country_id=country_id
                ).order_by('name')
            except (ValueError, TypeError):
                pass 
        elif self.instance.pk:
            self.fields['city'].queryset = City.objects.filter(
                country_id=(1, 2)
            ).order_by('name')


    class Media:
        css = {'all': ('css/bootstrap-datepicker3.standalone.css',)}
        js = (
            'js/bootstrap.bundle.min.js',
            'js/bootstrap-datepicker.js',
            )

    def clean_bio(self):
        """Ensure that bio info is greater than 10 and less than 1000
        characters
        """
        value = self.cleaned_data['bio']
        if len(value) < 10:
            raise forms.ValidationError(
                "We want to know you better! (10 characters or greater)")
        if len(value) > 1000:
            raise forms.ValidationError("Ok whoa, TMI! (1000 characters max)")
        return value
    
   
class AvatarForm(forms.ModelForm):
    """Form holding the user's avatar. We're using a separate form so 
    cropperjs can update outside of the other user data
    """
    class Meta:
        model = Profile
        fields = [
            'avatar',
        ]

    class Media:
        css = {'all': ('cropperjs/dist/cropper.css',)}
        js = ('cropperjs/dist/cropper.js',
              'jquery-cropper/dist/jquery-cropper.js',
              )


class UserForm(forms.Form):
    """Form that describes the user model (inherits from the standard 
    Django user model)
    """
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(UserForm, self).__init__(*args, **kwargs)

    first_name = forms.CharField(max_length=56)
    last_name = forms.CharField(max_length=56)


class ChangePasswordForm(forms.Form):
    """Form to validate and change user's password
    """
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(ChangePasswordForm, self).__init__(*args, **kwargs)

    password_help_text = {
        'same': 'must not be the same as the current password',
        'length': 'minimum password length of 14 characters',
        'lowercase': 'must contain lowercase letters',
        'uppercase': 'must contain uppercase letters',
        'digit': 'must include one or more numerical digits',
        'at': 'must contain @ sign',
        'pound': 'must contain # sign',
        'dollar': 'must contain $ sign',
        'username': 'cannot contain your username',
        'firstname': 'cannot contain your first name',
        'lastname': 'cannot contain your last name',
    }

    old_password = forms.CharField(label='Old password:',
                                   widget=forms.PasswordInput
                                   )
    new_password = forms.CharField(
        label='New password:',
        widget=forms.PasswordInput,
        help_text=password_help_text.values(),
        )                              
    new_password2 = forms.CharField(label='New password confirmation:',
                                    widget=forms.PasswordInput
                                    )

    def clean_old_password(self):
        """validate existing password
        """
        old_password = self.cleaned_data['old_password']
        if not self.user.check_password(old_password):
            raise forms.ValidationError("Your old password is incorrect!")
        return old_password

    def clean(self):
        """validate new passwords against valid regex patterns
        """
        cleaned_data = super().clean()
        old_pass = cleaned_data.get('old_password')
        new_pass = cleaned_data.get('new_password')
        new_pass2 = cleaned_data.get('new_password2')
        print(self.user.first_name)

        required_patterns = re.compile(r'''
            ^(?P<lowercase>[a-z]*) # return empty string if lowercase not found
            (?P<uppercase>[A-Z]*) # return empty string if uppercase not found
            (?P<digit>[0-9]*) # return empty string if digit not found
            (?P<at>@*) # return empty string if @ not found
            (?P<pound>\#*) # return empty string if # not found
            (?P<dollar>\$*)$ # return empty string if $ not found
        ''', re.X)

        forbidden_patterns = re.compile(r'''
            (?P<username>({username})*) # must not contain username
            (?P<firstname>({first})*) # must not contain first name
            (?P<lastname>({last})*) # must not contain last name
        '''.format(username=self.user.username,
                   first=self.user.first_name,
                   last=self.user.last_name),
                   re.X | re.I)

        required_result = required_patterns.search(new_pass2).groupdict()
        for key, value in required_result.items():
            if not value:
                msg = self.password_help_text[key]
                self.add_error('new_password', msg)
        
        forbidden_result = forbidden_patterns.search(new_pass2).groupdict()
        for key, value in forbidden_result.items():
            if value:
                msg = self.password_help_text[key]
                self.add_error('new_password', msg)

        if new_pass == old_pass:
            raise forms.ValidationError(
                "Your new password can't be your old password!"
            )

        if new_pass != new_pass2:
            raise forms.ValidationError("Your new passwords don't match!")

        if len(new_pass) < 14:
            msg = "Your new password must be minimum 14 characters."
            self.add_error('new_password', msg)
    