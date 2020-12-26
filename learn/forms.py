from django import forms
from .models import Lesson, Course

class ChallengeForm(forms.Form):
    challenge_link = forms.CharField(max_length=255, label='קישור לפרוייקט סקראץ:')


class LessonUpdateForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['title', 'description', 'pre_lesson', 'youtube',
                  'challenge_type', 'challenge', 'note']

    # Here we capture course_pk when it comes from CreateView
    # or from kwargs if it comes from UpdateView
    def __init__(self, course_pk=None, *args, **kwargs):
        print(f'course_pk: {course_pk}')
        if course_pk:
            course = Course.objects.get(pk=course_pk)
        else:
            course = kwargs['instance'].course
        super(LessonUpdateForm, self).__init__(*args, **kwargs)
        self.fields['pre_lesson'] = forms.ModelChoiceField(queryset=Lesson.objects.filter(course=course), required=False)
        # instance is the Lesson object passed here. you can filter upon it. -- filter(course=kwargs['instance'].course
