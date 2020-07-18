from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms
#from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from tinymce.widgets import TinyMCE
from .models import Profile

class UserCreateForm(UserCreationForm):
    email = forms.EmailField(required=True,
                         label='Email',
                         error_messages={'exists': 'Such email exists in the system'})

    #bio = forms.CharField(widget=TinyMCE(attrs={'cols': 80, 'rows': 30}))

    class Meta:
        fields = ("username", "email", "password1", "password2")
        model = get_user_model()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "User Name"
        self.fields["email"].label = "Email address"

    def save(self, commit=True):
        user = super(UserCreateForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user

    def clean_email(self):
        if get_user_model().objects.filter(email=self.cleaned_data['email']).exists():
            raise ValidationError(self.fields['email'].error_messages['exists'])
        return self.cleaned_data['email']


class EditProfileForm(forms.ModelForm):

    class Meta:
        model = get_user_model()
        fields = ('email','first_name','last_name')


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('bio', 'location', 'birth_date', 'image') #Note that we didn't mention user field here.
