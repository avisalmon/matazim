from django import forms
from .models import Project, Pic, Link
from django.utils.translation import ugettext_lazy as _


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'short_description', 'description', 'project_type', 'youtube']
        labels = {'title': _('כותרת'),
                  'short_description': _('תאור מקוצר'),
                  'description': _('תאור'),
                  'project_type': _('סוג הפרוייקט'),
                  }


class PicForm(forms.ModelForm):
    class Meta:
        model = Pic
        fields = ['title', 'image']
        lables = {
            'title': _('כותרת'),
            'image': _('תמונה'),
        }


class LinkForm(forms.ModelForm):
    class Meta:
        model = Link
        fields = ['title', 'link']
        labels = {
            'title': _('כותרת'),
            'link': _('קישור'),
        }
