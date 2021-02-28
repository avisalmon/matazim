from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.http import Http404
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView, CreateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from .models import Part, Item
from .forms import PartCreateForm, ItemUpdateForm

class PartListView(ListView):
    model = Part

class PartDetailView(DetailView):
    model = Part

class PartCreateView(LoginRequiredMixin, CreateView):
    model = Part
    form_class = PartCreateForm

class PartUpdateView(LoginRequiredMixin, UpdateView):
    model = Part
    fields = ['title', 'image', 'link', 'location', 'sub_location', 'mode',
              'price', 'contact', 'many', 'critical']

class PartDeleteView(LoginRequiredMixin, DeleteView):
    model = Part
    success_url = reverse_lazy('makerspace:part_list')

# *** Items ***

class ItemUpdateView(LoginRequiredMixin, UpdateView):
    model = Item
    form_class = ItemUpdateForm

@login_required
def create_more_items(request, part_pk):
    num = request.GET.get('num')

    try:
        part = Part.objects.get(pk=part_pk)
        for i in range(int(num)):
            Item.objects.create(part=part)
    except:
        pass

    return redirect('makerspace:part_detail', pk=part_pk)

class ItemDeleteView(LoginRequiredMixin, DeleteView):
    model = Item

    def get_success_url(self):
        return reverse_lazy('makerspace:part_detail', kwargs={'pk': self.object.part.pk})
