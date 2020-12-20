from django import forms
from .models import Lesson

class ChallengeForm(forms.Form):
    challenge_link = forms.CharField(max_length=255, label='קישור לפרוייקט סקראץ:')


class LessonUpdateForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['title', 'description', 'pre_lesson', 'youtube',
                  'challenge_type', 'challenge', 'note']

    def __init__(self, *args, **kwargs):
        super(LessonUpdateForm, self).__init__(*args, **kwargs)
        self.fields['pre_lesson'] = forms.ModelChoiceField(queryset=Lesson.objects.filter(course=kwargs['instance'].course), required=False)
        # instance is the Lesson object passed here. you can filter upon it.
