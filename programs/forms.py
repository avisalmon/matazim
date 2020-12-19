from django import forms
from .models import Program

# Not in use, seems like generated automatically in the CreatView. 
class ProgramForm(forms.ModelForm):
    class Meta:
        model = Program
        fields = ['name', 'short_description', 'description', 'link', 'image']
