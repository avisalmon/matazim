from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from .models import Course, Lesson, Registration, Completion
from main.models import Profile
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
import datetime
from django.contrib.admin.views.decorators import staff_member_required
import re
from django.contrib.auth import get_user_model

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
            completion.completed = datetime.datetime.now()
            completion.save()
    except:
        pass
    return redirect(completion)

def scratch_post(request, completion_pk):
    if request.method == 'GET':
        try:
            completion = Completion.objects.get(user=request.user, pk=completion_pk)
            completion.challenge_link = request.GET.get('sc_text')
            try:
                regex = re.compile(r'.*scratch.mit.edu/projects/(\d+)')
                match = regex.match(completion.challenge_link)
            except:
                pass

            if match:
                completion.challenge_link = match.group(1)
            else:
                completion.challenge_link = ""

            print(f'completion {completion}, {match.group(1)}, {completion.challenge_link}')
            completion.save()
        except:
            pass

    #return reverse('learn:completion_detail', kwargs={"pk": completion_pk})
    return redirect('learn:completion_detail', pk=completion_pk)


# def course_complete_message(request, registration_pk):
#     try:
#         registration = Registration.objects.get(pk=registration_pk)
#     except:
#         return redirect('home')
#
#     return render(request,
#                   'learn/complete_message.html',
#                   {'registration': registration })

@staff_member_required
def learnReport(request):
    context = {}
    context['profiles'] = Profile.objects.all()
    return render(request, 'learn/report.html', context)

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
