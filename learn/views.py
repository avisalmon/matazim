from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView, CreateView
from .models import Course, Lesson, Registration, Completion
from main.models import Profile
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
import datetime
from django.contrib.admin.views.decorators import staff_member_required
import re
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from .forms import LessonUpdateForm


def home(request):
    return render(request, 'learn/home.html')


class CourseListView(ListView):
    model=Course

    def get_context_data(self, **kwargs):
        context = super(CourseListView, self).get_context_data(**kwargs)
        try:
            courses_registered = Registration.objects.filter(user=self.request.user)
            context['courses_registered'] = courses_registered
            courses_names_for_user = [registration.course for registration in courses_registered]
            context['courses_names_for_user'] = courses_names_for_user
        except:
            pass
        return context


class CourseDetailView(DetailView):
    model=Course

    def get_context_data(self, **kwargs):
        context = super(CourseDetailView, self).get_context_data(**kwargs)
        try:
            user_course_completion_set = Completion.objects.filter(user=self.request.user,
                                                                   lesson__course=self.object)
            context['user_course_completion_set'] = user_course_completion_set
            courses_registered = Registration.objects.filter(user=self.request.user)
            context['courses_registered'] = courses_registered
            registration = Registration.objects.get(user=self.request.user,
            course=self.object)
            context['registration'] = registration
        except:
            pass

        # except Registration.DoesNotExist:
        #     registration = None

        return context


@login_required
def courseSignView(request, pk):
    try:
        course = Course.objects.get(pk=pk)
    except:
        redirect('learn:course_list')

    # create completions:
    for lesson in course.lessons.all():
        completion, created = Completion.objects.get_or_create(
            user=request.user,
            lesson=lesson)
            #defaults={'birthday': date(1940, 10, 9)},
        #completion.note = lesson.note
        completion.save()

    # asign pre conditions:
    for lesson in course.lessons.all():
        completion = Completion.objects.get(user=request.user,
                                            lesson=lesson)
        if lesson.pre_lesson:
            pre_completion = Completion.objects.get(user=request.user,
                                                    lesson=lesson.pre_lesson)
            completion.pre_completion = pre_completion
            completion.save()

    # set Registration to the course.
    try:
        registration = Registration(user=request.user,
                                course=course)
        registration.save()
    except:
        pass

    print('redirecting to course')
    return redirect(course)

@login_required
def course_unsign(request, pk):
    try:
        course = Course.objects.get(pk=pk)
        registration = Registration.objects.get(user=request.user,
                                               course=course)
        completions = Completion.objects.filter(lesson__course=course, user=request.user )
        for completion in completions:
            completion.delete()
    except:
        return redirect('home')

    registration.delete()
    return redirect('learn:course_list')

@login_required
def courseRate(request, pk, rate):
    try:
        course = Course.objects.get(pk=pk)
        registration = Registration.objects.get(user=request.user,
                                                course=course)
        print('Hi')
        if rate in range(6):
            registration.stars = rate
            registration.save()
        return redirect('learn:course_detail', pk=pk)
    except:
        print('Whoo')
        return redirect('learn:course_detail', pk=pk)


class CompletionDetailView(LoginRequiredMixin, DetailView):
    model=Completion

    def get_context_data(self, **kwargs):
        context = super(CompletionDetailView, self).get_context_data(**kwargs)
        user_course_completion_set = \
            Completion.objects.filter(user=self.request.user,
                                      lesson__course = self.object.lesson.course)
        courses_registered = Registration.objects.filter(user=self.request.user)
        context['courses_registered'] = courses_registered
        context['user_course_completion_set'] = user_course_completion_set
        try:
            registration = Registration.objects.get(user=self.request.user,
                                                    course=self.object.lesson.course)
            registration.last_completion = self.object
            registration.save()
        except Registration.DoesNotExist:
            registration = None

        context['registration'] = registration
        return context

class CourseCreateView(LoginRequiredMixin, CreateView):
    model = Course
    fields = ['title', 'short_description',
              'description', 'image', 'predecessor',
              'youtube']

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.owner = self.request.user
        obj.save()
        return super().form_valid(form)

class CourseUpdateView(LoginRequiredMixin, UpdateView):
    model = Course
    fields = ['title', 'short_description',
              'description', 'image', 'predecessor',
              'youtube']
    template_name = 'learn/course_update.html'

@login_required
def completion_done(request, pk):
    try:
        completion = Completion.objects.get(pk=pk)
    except:
        return redirect('home')
    completion.completed = datetime.datetime.now()
    completion.save()
    try:
        if completion.next_completion:
            completion = Completion.objects.get(pk=completion.next_completion.id)
            completion.completed = datetime.datetime.now()
            completion.save()
    except:
        pass
    return redirect(completion)

@login_required
def scratch_post(request, completion_pk):
    if request.method == 'GET':
        try:
            completion = Completion.objects.get(user=request.user, pk=completion_pk)
            completion.challenge_link = request.GET.get('sc_text')
            try:
                regex = re.compile(r'.*scratch.mit.edu/projects/(\d+)/embed')
                match = regex.match(completion.challenge_link)
            except:
                pass

            if match:
                print(1)
                completion.challenge_link = match.group(1)
            else:
                print(2)
                completion.challenge_link = ""

            completion.save()
        except:
            pass

    #return reverse('learn:completion_detail', kwargs={"pk": completion_pk})
    return redirect('learn:completion_detail', pk=completion_pk)

@login_required
def fusion_post(request, completion_pk):
    if request.method == 'GET':
        try:
            completion = Completion.objects.get(user=request.user, pk=completion_pk)
            completion.challenge_link = request.GET.get('in_text')
            try:
                regex = re.compile(r'.*autodesk360.com/shares/public/(.*)\?')
                match = regex.match(completion.challenge_link)
            except:
                pass

            if match:
                completion.challenge_link = match.group(1)
            else:
                completion.challenge_link = ""

            completion.save()
        except:
            pass

    #return reverse('learn:completion_detail', kwargs={"pk": completion_pk})
    return redirect('learn:completion_detail', pk=completion_pk)

@login_required
def tinkercad_post(request, completion_pk):
    if request.method == 'GET':
        try:
            completion = Completion.objects.get(user=request.user, pk=completion_pk)
            completion.challenge_link = request.GET.get('in_text')
            try:
                regex = re.compile(r'.*www.tinkercad.com/embed/(.*)\?')
                match = regex.match(completion.challenge_link)
            except:
                pass

            if match:
                completion.challenge_link = match.group(1)
            else:
                completion.challenge_link = ""

            completion.save()
        except:
            pass

    #return reverse('learn:completion_detail', kwargs={"pk": completion_pk})
    return redirect('learn:completion_detail', pk=completion_pk)

@staff_member_required
def learnReport(request):
    context = {}
    context['profiles'] = Profile.objects.all()
    return render(request, 'learn/report.html', context)

@login_required
def personal_report(request, pk): #pk for user
    user = get_user_model().objects.get(pk=pk)
    if user == request.user or request.user.is_staff:
        portfolio = [] # List --> dict {registration, [completions]}
        registrations = Registration.objects.filter(user=user)
        for registration in registrations:
            item = {}
            item['registration'] = registration

            item['completions'] = Completion.objects.filter(lesson__in=registration.course.lessons.all(), user=user)
            # build completion list for each registration
            portfolio.append(item)

        context = {}
        context['registrations'] = registrations
        context['portfolio'] = portfolio
        context['report_user'] = user
        return render(request, 'learn/personal_report.html', context)
    else:
        return redirect('home')


# class NoteUpdateView(LoginRequiredMixin, UpdateView):
#     model = Completion
#     fields = ['note']
#     template_name = 'learn/note_update.html'

class lessonCreateView(LoginRequiredMixin, CreateView):
    model = Lesson
    # fields = ['title', 'description', 'pre_lesson', 'youtube',
    #           'challenge_type', 'challenge', 'note']
    form_class = LessonUpdateForm

    def form_valid(self, form):
        obj = form.save(commit=False)
        course = Course.objects.get(pk=self.kwargs['course_pk'])
        print(course)
        obj.course = course
        obj.save()
        return super().form_valid(form)

class LessonUpdateView(LoginRequiredMixin, UpdateView):
    model = Lesson
    form_class = LessonUpdateForm
