from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from .models import Project, Pic, Link

class ProjectListView(ListView):
    model=Project


class ProjectDetailView(DetailView):
    model=Project
