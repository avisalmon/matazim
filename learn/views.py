from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView, CreateView, DeleteView
from .models import Course, Lesson, Registration, Completion, Batch, Order
from programs.models import Program
from .forms import LessonUpdateForm, CourseForm, FileForm, BatchForm
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
    first_completion = Completion.objects.filter(user=request.user,
                                                lesson__course=course)[0]
    print(first_completion)
    return redirect(first_completion)

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
    context['registration'] = registration


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
        context['form'] = FileForm
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

@login_required
def youtube_post(request, completion_pk):
    if request.method == 'GET':
        try:
            completion = Completion.objects.get(user=request.user, pk=completion_pk)
            completion.challenge_link = request.GET.get('in_text')

            regex = re.compile(r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|.+\?v=)?(?P<id>[A-Za-z0-9\-=_]{11})')
            match = regex.match(completion.challenge_link)
            if  match:
                completion.challenge_link = match.group('id')
            else:
                completion.challenge_link = ""

            completion.save()
        except:
            pass

    #return reverse('learn:completion_detail', kwargs={"pk": completion_pk})
    return redirect('learn:completion_detail', pk=completion_pk)

@login_required
def image_post(request, completion_pk):
    if request.method == 'POST':
        instance = Completion.objects.get(pk=completion_pk)
        form = FileForm(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            form.save()

    return redirect('learn:completion_detail', pk=completion_pk)

    #     try:
    #         completion = Completion.objects.get(user=request.user, pk=completion_pk)
    #         completion.image = request.FILES.get('myfile')
    #         print(completion.image)
    #         completion.save()
    #         print(2)
    #     except:
    #         pass
    #
    # #return reverse('learn:completion_detail', kwargs={"pk": completion_pk})
    # return redirect('learn:completion_detail', pk=completion_pk)


@staff_member_required
def learnReport(request):
    context = {}
    context['profiles'] = Profile.objects.all().order_by('-pk')
    return render(request, 'learn/report.html', context)

@login_required
def program_report(request, pk):
    context = {}
    try:
        program = Program.objects.get(pk=pk)
        context['program'] = program
        context['profiles'] = Profile.objects.filter(program_conn=program).order_by('-pk')
    except:
        pass
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

# ********* Batches and orders ***********
class BatchListView(LoginRequiredMixin, ListView):
    model = Batch

    def get_context_data(self, **kwargs):
        context = super(BatchListView, self).get_context_data(**kwargs)
        try:
            context['my_batches_orders'] = Batch.objects.filter(owner=self.request.user)
            context['my_batches_manufactor'] = Batch.objects.filter(suppliers__in=[self.request.user])
        except:
            pass
        return context


class BatchDetailView(LoginRequiredMixin, DetailView):
    model = Batch

    def get_context_data(self, **kwargs):
        context = super(BatchDetailView, self).get_context_data(**kwargs)
        try:
            context['orders'] = Order.objects.filter(batch=self.object)
        except:
            pass
        return context


class OrderCreateView(LoginRequiredMixin, CreateView):
    model = Order
    fields = ['address', 'name', 'email', 'phone', 'file' ]

    def dispatch(self, *args, **kwargs):
        print('dispatch')
        try:
            course = Course.objects.get(pk=self.kwargs['course_pk'])
            existing_order = Order.objects.get(user=self.request.user, course=course)
            if existing_order:
                print(f'found existing order {existing_order}')
                return redirect('learn:order_detail', pk=existing_order.pk)
        except:
            pass
        return super().dispatch(*args, **kwargs)

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.user = self.request.user
        try:
            course = Course.objects.get(pk=self.kwargs['course_pk'])
        except:
            raise Http404

        obj.course = course

        obj.check_if_approved()
        obj.save()

        return super().form_valid(form)

class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order

    def get_object(self):
        order = super(OrderDetailView, self).get_object()
        order.check_if_approved()
        order.save()
        return order

    def get_context_data(self, **kwargs):
        context = super(OrderDetailView, self).get_context_data(**kwargs)
        # self.object.check_if_approved()
        context['form'] = BatchForm
        try:
            batches = Batch.objects.all()
            context['batches'] = batches
        except:
            pass

        return context


class OrderUpdateView(LoginRequiredMixin, UpdateView):
    model=Order
    fields = ['address', 'name', 'email', 'phone', 'file']

    def get_object(self):
        order = super(OrderUpdateView, self).get_object()
        if not order.user == self.request.user:
            raise Http404('You dontt have permission to do this. go away you hacker')
        return order


class OrderAdminList(LoginRequiredMixin, ListView):
    model=Order
    template_name = 'learn/order_admin_list.html'

    def dispatch(self, *args, **kwargs):
        if not (self.request.user.is_staff or self.request.user.profile.is_supplier):
            return redirect('/')
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(OrderAdminList, self).get_context_data(**kwargs)
        try:
            context['ready_orders'] = Order.objects.filter(error='', batch=None)
            context['not_ready_orders'] = Order.objects.exclude(error='')
            batches = Batch.objects.all()
            for batch in batches:
                batch.update_batch()
                batch.save()
            context['batches'] = batches
            if self.request.user.profile.is_supplier:
                print('Supplier quiery')
                context['supplier_batches'] = Batch.objects.filter(suppliers__in=[self.request.user])
        except:
            pass
        return context

def assign_to_batch(request, order_pk):
    if request.method == 'POST':
        print('**** starting updates...')
        try:
            order = Order.objects.get(pk=order_pk)
            print(f'the order to process {order} ')
        except:
            print('Cound not find the order')
            return redirect('learn:order_detail', pk=order_pk)

        print('checking for old batch')
        old_batch = False
        if order.batch:
            try:
                old_batch = Batch.objects.get(pk=order.batch.pk)
                print(f'got the old batch {old_batch}')
            except:
                print('Could not find old batch')
                return redirect('learn:order_detail', pk=order_pk)

        form = BatchForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            # order now has the new batch updated.
            try:
                print('updating batches...')
                new_batch = Batch.objects.get(pk=order.batch.pk)
                print(f'the new batch is now {new_batch}')
                orders_of_new_batch = Order.objects.filter(batch=order.batch)
                len_of_new_batch = len(orders_of_new_batch)
                print('Updating new batch')
                new_batch.update_batch()
                new_batch.save()
                if old_batch:
                    print('updating old batch')
                    old_batch.update_batch()
                    old_batch.save()
            except:
                print('Error in updating batches')

    return redirect('learn:order_admin_list')

def order_remove_batch(request, order_pk):
    try:
        order = Order.objects.get(pk=order_pk)
        if order.batch:
            order.batch = None
        order.save()
    except:
        pass

    return redirect('learn:order_admin_list')

def order_mark_printed(request, order_pk):
    try:
        print(order_pk)
        order = Order.objects.get(pk=order_pk)
        print('whh')
        order.printed = True
        order.save()
    except:
        pass

    return redirect('learn:order_admin_list')

def order_mark_unprinted(request, order_pk):
    try:
        print(order_pk)
        order = Order.objects.get(pk=order_pk)
        order.printed = False
        order.save()
    except:
        pass

    return redirect('learn:order_admin_list')

def order_mark_sent(request, order_pk):
    try:
        print(order_pk)
        order = Order.objects.get(pk=order_pk)
        order.sent = True
        order.sent_date = datetime.datetime.now()
        order.save()
    except:
        pass

    return redirect('learn:order_admin_list')

def order_mark_unsent(request, order_pk):
    try:
        print(order_pk)
        order = Order.objects.get(pk=order_pk)
        order.sent = False
        order.sent_date = None
        order.save()
    except:
        pass

    return redirect('learn:order_admin_list')
