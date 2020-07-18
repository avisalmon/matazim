from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.urls import reverse_lazy
from django.views.generic import CreateView
from . import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
#from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from django.views.generic import (DetailView, UpdateView)
from .models import Profile
from .forms import EditProfileForm, ProfileForm


def home(request):
    return render(request, 'main/home.html')


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
            return redirect('home')

        else:
            error = form.errors
            return render(request, 'registration/signup.html', {'form':forms.UserCreateForm(), 'error': error})

        # if request.POST['password1'] == request.POST['password2']:
        #     try:
        #         user = User.objects.create_user(request.POST['username'], password=request.POST['password1'])
        #         user.save()
        #         login(request, user)
        #         return redirect('home')
        #     except IntegrityError:
        #         return render(request,
        #                       'main/signuplocal.html',
        #                       {'form':UserCreationForm(),
        #                        'error':'That username has already been taken. Please choose a new username'})
        # else:
        #     return render(request, 'main/signup_local.html', {'form':UserCreationForm(), 'error':'Passwords did not match'})


@login_required
def my_profile_view(request):
    profile = Profile.objects.get(user=request.user)
    context = {
        'profile': profile
    }
    template = 'main/profile.html'
    return render(request, template, context)

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)  # request.FILES is show the selected image or file
        print('Hi')
        if form.is_valid() and profile_form.is_valid():
            user_form = form.save()
            custom_form = profile_form.save(False)
            custom_form.user = user_form
            custom_form.save()
            return redirect('main:my_profile_view')
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

def profile_view(request, profile_pk):
    profile = get_object_or_404(Profile, pk=profile_pk)
    context = {
        'profile': profile
    }
    template = 'main/profile_details.html'
    return render(request, template, context)
