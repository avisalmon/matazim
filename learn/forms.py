from django import forms

class ChallengeForm(forms.Form):
    challenge_link = forms.CharField(max_length=255, label='קישור לפרוייקט סקראץ:')
