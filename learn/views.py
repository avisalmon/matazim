from django.shortcuts import render, redirect
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from .models import Course, Lesson, Registration, Completion
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
import datetime

def home(request):
    return render(request, 'learn/home.html')


class CourseListView(ListView):
    model=Course

    def get_context_data(self, **kwargs):
        context = super(CourseListView, self).get_context_data(**kwargs)
        courses_registered = Registration.objects.filter(user=self.request.user)
        context['courses_registered'] = courses_registered
        return context


class CourseDetailView(LoginRequiredMixin, DetailView):
    model=Course

    def get_context_data(self, **kwargs):
        context = super(CourseDetailView, self).get_context_data(**kwargs)
        user_course_completion_set = Completion.objects.filter(user=self.request.user,
                                                               lesson__course=self.object)
        context['user_course_completion_set'] = user_course_completion_set
        courses_registered = Registration.objects.filter(user=self.request.user)
        context['courses_registered'] = courses_registered
        #print(self.object.owner)
        try:
            registration = Registration.objects.get(user=self.request.user,
                                                    course=self.object)
        except Registration.DoesNotExist:
            registration = None

        context['registration'] = registration
        return context


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

    # asign pre conditions:
    for lesson in course.lessons.all():
        completion = Completion.objects.get(user=request.user,
                                            lesson=lesson)
        print(completion)
        if lesson.pre_lesson:
            print('There is pre_lesson')
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

    return redirect(course)


def course_unsign(request, pk):
    try:
        course = Course.objects.get(pk=pk)
        registration = Registration.objects.get(user=request.user,
                                               course=course)
        print('Hi')
    except:
        return redirect('home')

    registration.delete()
    return redirect('learn:course_list')


class CompletionDetailView(DetailView):
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
    except:
        pass
    return redirect(completion)


# def course_complete_message(request, registration_pk):
#     try:
#         registration = Registration.objects.get(pk=registration_pk)
#     except:
#         return redirect('home')
#
#     return render(request,
#                   'learn/complete_message.html',
#                   {'registration': registration })
