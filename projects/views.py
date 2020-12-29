from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.http import Http404
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView, CreateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from .models import Project, Pic, Link
from .forms import ProjectForm, PicForm, LinkForm

class ProjectListView(ListView):
    model = Project


class ProjectDetailView(DetailView):
    model = Project


class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.owner = self.request.user
        obj.save()
        return super().form_valid(form)


class ProjectUpdateView(LoginRequiredMixin, UpdateView):
    model = Project
    form_class = ProjectForm

    def get_object(self):
        project = super(ProjectUpdateView, self).get_object()
        if not project.owner == self.request.user:
            raise Http404('You dontt have permission to do this. go away you hacker')
        return project


class ProjectDeleteView(LoginRequiredMixin, DeleteView):
    model = Project
    success_url = reverse_lazy('projects:project_list')

    def get_object(self):
        project = super(ProjectDeleteView, self).get_object()
        if not project.owner == self.request.user:
            raise Http404('You dontt have permission to do this. go away you hacker')
        return project


@login_required
def add_pic(request, project_pk):
    try:
        project = Project.objects.get(owner=request.user, pk=project_pk)
    except:
        raise Http404

    if request.method == 'POST':
        form = PicForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.project = project
            obj.save()
            return redirect('projects:project_detail', pk=project_pk)
    else:
        form = PicForm()

    return render(request, 'projects/add_pic.html', {'form': form})

@login_required
def add_link(request, project_pk):
    try:
        project = Project.objects.get(owner=request.user, pk=project_pk)
    except:
        raise Http404

    if request.method == 'POST':
        form = LinkForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.project = project
            obj.save()
            return redirect('projects:project_detail', pk=project_pk)
    else:
        form = LinkForm()

    return render(request, 'projects/add_link.html', {'form': form})

@login_required
def img_delete(request, pk):
    try:
        img = Pic.objects.get(project__owner=request.user, pk=pk)
    except:
        raise Http404

    project = img.project

    img.image.delete() # this removes the media file
    img.delete()
    return redirect(project)

@login_required
def link_delete(request, pk):
    try:
        link = Link.objects.get(project__owner=request.user, pk=pk)
    except:
        raise Http404

    project = link.project
    link.delete()
    return redirect(project)
