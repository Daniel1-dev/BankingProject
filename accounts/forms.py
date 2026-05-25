from django import forms
from .models import Profile, Note, Contribution
from django.contrib.auth.models import User



class UserUpdateForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ['username', 'email']


class ProfileUpdateForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = ['profile_picture', 'bio']


class NoteForm(forms.ModelForm):

    class Meta:
        model = Note
        fields = ['title', 'content']
        



class ContributionForm(forms.ModelForm):

    class Meta:

        model = Contribution

        fields = [
            'amount'
        ]