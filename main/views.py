from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from django.contrib.auth import login, logout
from django.urls import reverse_lazy
# from django.views.generic import
from django.views.generic.edit import DeleteView, UpdateView, CreateView
from . import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
#from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from django.views.generic import (DetailView, UpdateView)
from .models import Profile, UserHobby, Status
from learn.models import Registration, Course
from projects.models import Project
from programs.models import Program
from .forms import EditProfileForm, ProfileForm, HobbyForm
from django.http import JsonResponse
from django.core import serializers
from django.contrib.auth.mixins import LoginRequiredMixin

# ******************** Home **********************

def home(request):
    return render(request, 'main/home.html')

def search(request):
    context = {}
    if request.method == 'GET':
        print('Get')
        term = request.GET.get('term')
        context['term'] = term

        profiles1 = Profile.objects.filter(user__username__icontains=term)
        profiles2 = Profile.objects.filter(user__email__icontains=term)
        profiles3 = Profile.objects.filter(user__first_name__icontains=term)
        profiles4 = Profile.objects.filter(user__last_name__icontains=term)
        profiles = profiles1.union(profiles2).union(profiles3).union(profiles4)
        context['profiles'] = profiles

        programs1 = Program.objects.filter(name__icontains=term)
        programs2 = Program.objects.filter(short_description__icontains=term)
        programs = programs1.union(programs2)
        context['programs'] = programs

        courses1 = Course.objects.filter(title__icontains=term)
        courses2 = Course.objects.filter(short_description__icontains=term)
        courses3 = Course.objects.filter(description__icontains=term)
        courses = courses1.union(courses2).union(courses3)
        context['courses'] = courses
    else:
        print('bla')

    return render(request, 'main/search.html', context )


# ********************* Auth *********************

def signup(request):
    if request.method == 'GET':
        return render(request, 'registration/signup.html', {'form':forms.UserCreateForm()})
    else:
        form = forms.UserCreateForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            email = form.cleaned_data.get('email')
            authenticate( username=username,password=raw_password, backend='django.contrib.auth.backends.ModelBackend')
            user = get_user_model().objects.get(username=username)
            print(f'Login 0 - {user}')
            login(request, user)
            print('Login 1')
            if request.GET.get('next'):
                print('Got into get')
                print(request.GET.get('next'))
            return redirect('home')

        else:
            error = form.errors
            return render(request, 'registration/signup.html', {'form':forms.UserCreateForm(), 'error': error})

# ********************** Profile *********************

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)  # request.FILES is show the selected image or file

        if form.is_valid() and profile_form.is_valid():
            user_form = form.save()
            custom_form = profile_form.save(False)
            custom_form.user = user_form
            custom_form.save()
            return redirect('main:profile', profile_pk=request.user.profile.pk)
        else:
            context = {}
            context['form'] = EditProfileForm(instance=request.user)
            context['profile_form'] = ProfileForm(instance=request.user.profile)
            context['errors'] = 'You got errors. Try again'
            return render(request, 'main/edit_profile.html', context)

    else:
        form = EditProfileForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)
        context = {}
        # args.update(csrf(request))
        context['form'] = form
        context['profile_form'] = profile_form
        return render(request, 'main/edit_profile.html', context)

@login_required
def profile_view(request, profile_pk):
    if profile_pk == 0:
        profile_pk = request.user.profile.pk
    profile = get_object_or_404(Profile, pk=profile_pk)
    context = {
        'profile': profile
    }
    try:
        courses_registered = Registration.objects.filter(user=profile.user)
        context['courses_registered'] = courses_registered
        statuses = Status.objects.filter(user=profile.user)
        context['statuses'] = statuses
        context['badges'] = range(1, int(profile.level)+1)
    except:
        pass

    try:
        projects = Project.objects.filter(owner=profile.user)
        context['projects'] = projects
    except:
        pass

    context['hobby_form'] = HobbyForm
    template = 'main/profile_details.html'
    return render(request, template, context)

def add_badge(request, profile_pk, badge):
    try:
        profile = Profile.objects.get(pk=profile_pk)
        if badge in range(7):
            profile.level = badge
            profile.save()
    except:
        pass

    return redirect('main:profile', profile_pk=profile_pk)


class AddUserToProgram(LoginRequiredMixin, UpdateView):
    model = Profile
    fields = ['program_conn']
    template_name_suffix = '_program_update_form'


class ProfileStuffUpdate(LoginRequiredMixin, UpdateView):
    model = Profile
    fields = ['location', 'perach', 'mataz', 'mentor', 'top_goal', 'program_conn']
    template_name_suffix = '_staff_form'

    def form_valid(self, form):
        obj = form.save(commit=False)
        writer_profile = get_object_or_404(Profile, pk=self.request.user.profile.pk)
        if not ( writer_profile.user.is_staff):
            raise Http404('You dont have permission to do this.')
        return super().form_valid(form)


# **************** Hobby views *************************

@login_required
def add_hobby(request):
    if request.is_ajax and request.method == 'POST':
        form = HobbyForm(request.POST)
        if form.is_valid():
            instance = form.save(False)
            instance.user = request.user
            instance.save()
            ser_instance = serializers.serialize('json', [ instance, ])
            return JsonResponse({"instance": ser_instance}, status=200)
        else:
            #some form errors:
            print('oops')
            return JsonResponse({"error": form.errors}, status=400)

    # an error accured:
    return JsonResponse({"error": ""}, status=400)


class HobbyDeleteView(LoginRequiredMixin, DeleteView):
    model = UserHobby
    success_url = reverse_lazy('main:profile', kwargs={'profile_pk': 0})


class HobbyUpdateView(LoginRequiredMixin, UpdateView):
    model = UserHobby
    fields = ['title', 'description']
    template_name_suffix = '_update_form'

    def dispatch(self, request, *args, **kwargs):
        """" Making sure that only owners can update """
        obj = self.get_object()
        if obj.user != self.request.user:
            return redirect('programs:facilitator_list')
        return super(HobbyUpdateView, self).dispatch(request, *args, **kwargs)

# Status Views

class StatusCreateForm(LoginRequiredMixin, CreateView):
    model = Status
    fields = ['text', 'image']

    def form_valid(self, form):
        obj = form.save(commit=False)
        for_profile = get_object_or_404(Profile, pk=self.kwargs['for_profile_pk'])
        writer_profile = get_object_or_404(Profile, pk=self.request.user.profile.pk)
        if not ( writer_profile.user.is_staff or writer_profile.user == self.request.user):
            raise Http404('You dont have permission to do this.')
        obj.written_by = writer_profile.user
        obj.user = for_profile.user
        obj.save()
        return super().form_valid(form)

class StatusUpdateView(LoginRequiredMixin, UpdateView):
    model = Status
    fields = ['text', 'image']

    def form_valid(self, form):
        obj = form.save(commit=False)
        for_profile = obj.user.profile
        writer_profile = get_object_or_404(Profile, pk=self.request.user.profile.pk)
        if not ( writer_profile.user.is_staff or writer_profile.user == self.request.user):
            raise Http404('You dont have permission to do this.')
        return super().form_valid(form)

class StatusDeleteView(LoginRequiredMixin, DeleteView):
    model = Status

    def get_success_url(self):
    # Assuming there is a ForeignKey from Comment to Post in your model
        profile = self.object.user.profile
        return reverse_lazy( 'main:profile', kwargs={'profile_pk': profile.pk})
