from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from reading.models import Category

from .models import UserProfile


class SignUpForm(UserCreationForm):
    display_name = forms.CharField(label="Nome de exibicao", max_length=80, required=False)
    interests = forms.ModelMultipleChoiceField(
        label="Interesses",
        queryset=Category.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "display_name", "interests")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["interests"].queryset = Category.objects.filter(is_active=True)

    def save(self, commit=True):
        user = super().save(commit=commit)

        if commit:
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.display_name = self.cleaned_data.get("display_name", "")
            profile.save()
            profile.interests.set(self.cleaned_data.get("interests", []))

        return user


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ("display_name", "current_level", "avatar", "interests")
        widgets = {
            "interests": forms.CheckboxSelectMultiple,
        }
