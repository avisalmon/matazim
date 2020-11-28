from django.shortcuts import render
from django.views.generic.list import ListView
from .models import Hack, Team, Schedule, Rating, Comment


def home(request):
    return render(request, 'hack/home.html')


class HackListView(ListView):
    model=Hack
