from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile, UserSkill, ExchangeRequest, Session, Review

class RegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150, required=False)
    email = forms.EmailField()
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "first_name", "last_name", "email")

class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150, required=False)
    email = forms.EmailField()
    class Meta:
        model = UserProfile
        fields = ("department", "year", "bio", "profile_image", "availability")

class UserSkillForm(forms.ModelForm):
    skill_name = forms.CharField(max_length=100, label="Skill")
    class Meta:
        model = UserSkill
        fields = ("skill_type", "level")

class RequestForm(forms.ModelForm):
    class Meta:
        model = ExchangeRequest
        fields = ("message",)
        widgets = {"message": forms.Textarea(attrs={"rows": 3, "placeholder": "What would you like to learn?"})}

class SessionForm(forms.ModelForm):
    class Meta:
        model = Session
        fields = ("date", "time", "notes")
        widgets = {"date": forms.DateInput(attrs={"type": "date"}), "time": forms.TimeInput(attrs={"type": "time"})}

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ("rating", "comment")
        widgets = {"comment": forms.Textarea(attrs={"rows": 3})}
