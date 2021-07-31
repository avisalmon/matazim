from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView, CreateView, DeleteView
from .models import Course, Lesson, Registration, Completion
from .forms import LessonUpdateForm, CourseForm
from main.models import Profile
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from .serializers import CourseSerializer
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
import re
import datetime


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
        completion.note = lesson.note
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
def course_confirm_unsign(request, pk):
    try:
        course = Course.objects.get(pk=pk)
        registration = Registration.objects.get(user=request.user,
                                               course=course)
    except:
        return redirect('home')

    context={}
    context['course'] = course
    # context['registration'] = registration


    return render(request, 'learn/course_confirm_delete.html', context)


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
def update_lessons(request, registration_pk):
    registration = get_object_or_404(Registration, pk=registration_pk)
    if registration.user != request.user:
        raise Http404('You dontt have permission to do this. go away you hacker')

    current_completions = Completion.objects.filter(user=request.user, lesson__course=registration.course)
    current_lessons = [completion.lesson for completion in current_completions]
    expected_lessons = Lesson.objects.filter(course=registration.course)

    for expected_lesson in expected_lessons:
        if expected_lesson not in current_lessons:
            #create completion
            completion = Completion.objects.create(
                user=request.user,
                lesson=expected_lesson)
                #defaults={'birthday': date(1940, 10, 9)},
            completion.note = expected_lesson.note
            print(f'pre_lesson {completion.lesson.pre_lesson}')
            if completion.lesson.pre_lesson:
                try:
                    pre_completion = Completion.objects.get(user=request.user,
                                                            lesson=completion.lesson.pre_lesson)
                    completion.pre_completion = pre_completion
                except:
                    pass
            completion.save()

    return redirect(request.META['HTTP_REFERER'])



@login_required
def courseRate(request, pk, rate):
    next = request.GET.get('next')
    try:
        course = Course.objects.get(pk=pk)
        registration = Registration.objects.get(user=request.user,
                                                course=course)
        if rate in range(6):
            registration.stars = rate
            registration.save()
        if next:
            return redirect(next)
        else:
            return redirect('learn:course_detail', pk=pk)
    except:
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
    form_class = CourseForm

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.owner = self.request.user
        obj.save()
        return super().form_valid(form)

class CourseUpdateView(LoginRequiredMixin, UpdateView):
    model = Course
    form_class = CourseForm
    template_name = 'learn/course_update.html'

    def get_object(self):
        course = super(CourseUpdateView, self).get_object()
        if not course.owner == self.request.user:
            raise Http404('You dontt have permission to do this. go away you hacker')
        return course

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
    context['profiles'] = Profile.objects.all().order_by('-pk')
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


class NoteUpdateView(LoginRequiredMixin, UpdateView):
    model = Completion
    fields = ['note']
    template_name = 'learn/note_update.html'

    def get_object(self):
        completion = super(NoteUpdateView, self).get_object()
        if not completion.user == self.request.user:
            raise Http404('You dontt have permission to do this. go away you hacker')
        return completion

class lessonCreateView(LoginRequiredMixin, CreateView):
    model = Lesson
    # fields = ['title', 'description', 'pre_lesson', 'youtube',
    #           'challenge_type', 'challenge', 'note']
    form_class = LessonUpdateForm

    def form_valid(self, form):
        obj = form.save(commit=False)
        course = Course.objects.get(pk=self.kwargs['course_pk'])
        if not course.owner == self.request.user:
            raise Http404
        obj.course = course
        obj.save()
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super(lessonCreateView, self).get_form_kwargs()
        # update the kwargs for the form init method with URL params
        # in this case course_pk will be passed to the form __init__
        kwargs.update(self.kwargs)  # self.kwargs contains all url conf params
        return kwargs

class LessonUpdateView(LoginRequiredMixin, UpdateView):
    model = Lesson
    form_class = LessonUpdateForm

    def form_valid(self, form):
        obj = form.save(commit=False)
        print(obj)
        if not obj.course.owner == self.request.user:
            raise Http404
        # place holder
        return super().form_valid(form)

# **************** API ******************

class CourseViewSet(viewsets.ModelViewSet):
    serializer_class = CourseSerializer
    queryset = Course.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    # in postman Authorization Token blabla
