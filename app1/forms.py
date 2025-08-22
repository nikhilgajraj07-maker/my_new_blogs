from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Blogs, Feedback, ContactMessage, Profile
from django.utils.html import strip_tags
import re
import bleach


class BlogsForms(forms.ModelForm):  # Keep original name so views don't break
    class Meta:
        model = Blogs
        fields = ['title', 'content', 'image']  # author excluded, handled in view
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control form-control-lg shadow-sm rounded-3 border-0',
                'placeholder': 'Enter a catchy blog title...',
                'style': 'font-size:1.1rem;'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control d-none',  # Hidden because Quill will handle it
                'rows': 5
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control shadow-sm rounded-3 border-0',
                'style': 'padding:10px;'
            }),
        }
        labels = {
            'title': 'Blog Title',
            'image': 'Featured Image',
            'content': 'Content'
        }

    def clean_content(self):
        raw_html = (self.data.get('content') or '').strip()
        text = strip_tags(raw_html)
        text = text.replace('&nbsp;', ' ').replace('\xa0', ' ')
        text_no_space = re.sub(r'\s+', '', text)

        if not text_no_space:
            raise forms.ValidationError("Content cannot be empty.")
        return raw_html


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['name', 'email', 'message']


class ContactForm(forms.ModelForm):  # Keep name same as your original code
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'message']


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'})
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
    )
    image = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email','password1', 'password2')

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Username'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirm Password'})

    
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['image']
        widgets = {
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'})
        }

    def save(self, commit=True):
        profile = super().save(commit=False)
        if commit:
            profile.save()
        return profile


class UserProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=False, label="First Name")
    last_name = forms.CharField(max_length=30, required=False, label="Last Name")
    email = forms.EmailField(required=False, label="Email Address")

    class Meta:
        model = Profile
        fields = ['image', 'first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['email'].initial = user.email

    def save(self, commit=True):
        profile = super().save(commit=False)
        user = profile.user
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            profile.save()
        return profile