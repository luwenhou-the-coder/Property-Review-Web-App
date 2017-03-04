from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from studentnest.models import *
from studentnest.arrays import UNI_CHOICES,MAJOR_CHOICES
import re

class RegistrationForm(forms.Form):
    username = forms.CharField(max_length=30, label='Email', widget=forms.EmailInput(attrs={'placeholder': 'must be student email'}))
    password1 = forms.CharField(max_length=20, label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(max_length=20, label='Confirm Password', widget=forms.PasswordInput)
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    university = forms.ChoiceField(choices=UNI_CHOICES,initial="")
    major = forms.ChoiceField(choices=MAJOR_CHOICES,initial="")

    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()

        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Password doesn't match.")

        return cleaned_data

    def clean_username(self):
        cleaned_data = super(RegistrationForm, self).clean()

        username = cleaned_data.get('username')
        if not username.endswith('.edu'):
            raise forms.ValidationError("Not a valid student email address.")

        if User.objects.filter(username__exact=username):
            raise forms.ValidationError("Email address already taken.")

        return username


class LoginForm(forms.Form):
    username = forms.CharField(max_length=100, label='Email', widget=forms.EmailInput)
    password = forms.CharField(max_length=100, widget=forms.PasswordInput)
    
    def clean(self):
        cleaned_data = super(LoginForm, self).clean()

        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if not User.objects.filter(username__exact=username):
            raise forms.ValidationError("Email address doesn't exist.")

        if User.objects.get(username=username).is_active == False:
            raise forms.ValidationError("Account is not activated yet.")

        user = authenticate(username=username, password=password)

        if user is None:
            raise forms.ValidationError("Invalid password.")

        return cleaned_data


class PublishForm(forms.ModelForm):
    CHOICES = (('HOUSE', 'House'), ('APARTMENT', 'Apartment'), ('TOWNHOUSE', 'Townhouse'),)
    type = forms.ChoiceField(choices=CHOICES,initial="")

    class Meta:
        model = Property
        exclude = ('rating','latitude','longitude','publisher',)
        labels = {
            'min_bedroom_num': 'Min bedroom num (1 ~ 20)',
            'max_bedroom_num': 'Max bedroom num (1 ~ 20)',
        }
        widgets = {'picture':forms.FileInput(),
                   'min_bedroom_num': forms.NumberInput(attrs={'min': '1', 'max': '20'}),
                   'max_bedroom_num': forms.NumberInput(attrs={'min': '1', 'max': '20'}),
                   'description':forms.Textarea(attrs={'cols': 30, 'rows': 10}),
                   'contact_phone': forms.TextInput(attrs={'placeholder' : '000-000-0000'})
                   }

    def clean(self):
        cleaned_data = super(PublishForm, self).clean()

        min_bedroom_num = cleaned_data.get('min_bedroom_num')
        max_bedroom_num = cleaned_data.get('max_bedroom_num')

        if min_bedroom_num > max_bedroom_num:
            raise forms.ValidationError("Min bedroom number cannot be greater than max bedroom number.")

        return cleaned_data

    def clean_price(self):
        price = self.cleaned_data.get('price')

        if price <= 0:
            raise forms.ValidationError("Price must be greater than 0.")

        return price

    def clean_contact_phone(self):
        contact_phone = self.cleaned_data.get('contact_phone')

        if not re.match(r'^[0-9]{3}-[0-9]{3}-[0-9]{4}$', contact_phone):
            raise forms.ValidationError("Contact phone is not valid.")

        return contact_phone

    def clean_zip(self):
        zip = self.cleaned_data.get('zip')

        if not re.match(r'^[0-9]{5}$', zip):
            raise forms.ValidationError("Zip code is not valid.")

        return zip


class ImageForm(forms.ModelForm):
    property_image = forms.ImageField(label='Image')
    class Meta:
	model = PropertyImage
	fields = ('property_image',)

class ProfileForm(forms.ModelForm):
    university = forms.ChoiceField(choices=UNI_CHOICES)
    major = forms.ChoiceField(choices=MAJOR_CHOICES)
    gender = forms.ChoiceField(choices=(('',''),('M', 'Male'), ('F', 'Female')), initial="", required=False)
    class Meta:
        model = Profile
        fields = ('age', 'gender', 'university', 'major', 'profile_images')
        labels = {
            'major': 'Major',
            'profile_images': 'Avatar',
        }
        widgets = {
            'age': forms.NumberInput(attrs={'min': '0'}),
            'profile_images': forms.FileInput(),
        }

    def clean_age(self):
        age = self.cleaned_data.get('age')

        if age and age < 0:
            raise forms.ValidationError("Age cannot be negative.")

        return age


class ChangePasswordForm(forms.Form):
    original_password = forms.CharField(max_length=40, label='Original Password', widget=forms.PasswordInput())
    new_password1 = forms.CharField(max_length=40, label='New password', widget=forms.PasswordInput())
    new_password2 = forms.CharField(max_length=40, label='Confirm Password', widget=forms.PasswordInput())

    def clean(self):
        # Calls our parent (forms.Form) .clean function, gets a dictionary
        # of cleaned data as a result
        cleaned_data = super(ChangePasswordForm, self).clean()

        # Confirms that the two password fields match
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')
        if new_password1 and new_password2 and new_password1 != new_password2:
            raise forms.ValidationError('New Passwords did not match.')

        # Generally return the cleaned data we got from our parent.
        return cleaned_data


class reviewForm(forms.Form):
    content = forms.CharField(max_length=400)

    def clean(self):
        cleaned_data = super(reviewForm, self).clean()

        return cleaned_data

class ResetForm(forms.Form):
    username = forms.CharField(max_length = 100, label = 'Email', widget=forms.EmailInput)
    def clean(self):
        cleaned_data = super(ResetForm, self).clean()
	username = cleaned_data.get('username')
	if not User.objects.filter(username__exact=username):
	    raise forms.ValidationError("Email address does not exist.")
        return cleaned_data

class ResetConfirmForm(forms.Form):
    password1 = forms.CharField(max_length = 100, label = 'New Password', widget=forms.PasswordInput)
    password2 = forms.CharField(max_length = 100, label = 'Confirm Password', widget=forms.PasswordInput)
    def clean(self):
        cleaned_data = super(ResetConfirmForm, self).clean()

	password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
	if password1 and password2 and password1 != password2:
	    raise forms.ValidationError("Passwords not match.")
        return cleaned_data
