from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.http import Http404
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView, CreateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from bootstrap_datepicker_plus import DateTimePickerInput, DatePickerInput
from .models import Contact, Note


class ContactCreateForm(LoginRequiredMixin, CreateView):
    model = Contact
    fields = ['name', 'description', 'email', 'link', 'strategic_comment',
              'next_step', 'tizkoret', 'phone']

    # Date Picker reference:
    # https://django-bootstrap-datepicker-plus.readthedocs.io/en/latest/Usage.html#types-of-datepickers
    def get_form(self):
        form = super().get_form()
        form.fields['tizkoret'].widget = DatePickerInput()
        form.fields['tizkoret'].label = 'תזכורת'
        return form

    def form_valid(self, form):
        if not self.request.user.is_staff:
            raise Http404('You dontt have permission to do this. go away you hacker')
        return super().form_valid(form)


class ContactListView(LoginRequiredMixin, ListView):
    model = Contact

    def dispatch(self, request, *args, **kwargs):
            if not request.user.is_staff:
                raise Http404('You dontt have permission to do this. go away you hacker')
            return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ContactListView, self).get_context_data(**kwargs)
        try:
            urjent_actions = Contact.objects.filter(tizkoret__lte=datetime.date.today()).order_by('-tizkoret')
            context['urjent_actions'] = prioritized
            todo_actions = Contact.objects.filter(tizkoret__gt=datetime.date.today()).order_by('-tizkoret')
            context['todo_actions'] = todo_actions
            other_contacts = Contact.objects.filter(tizkoret__isnull=True).order_by('name')
            context['other_contacts'] = other_contacts
            master_stages = MasterStage.objects.all()
            context['master_stages'] = master_stages
            print(master_stages)
        except:
            pass

        # except Registration.DoesNotExist:
        #     registration = None

        return context


class ContactDetailView(LoginRequiredMixin, DetailView):
    model = Contact

    def dispatch(self, request, *args, **kwargs):
            if not request.user.is_staff:
                raise Http404('You dontt have permission to do this. go away you hacker')
            return super().dispatch(request, *args, **kwargs)


class ContactUpdateView(LoginRequiredMixin, UpdateView):
    model = Contact
    fields = ['name', 'description', 'email', 'link', 'strategic_comment',
              'next_step', 'tizkoret', 'phone']

    def dispatch(self, request, *args, **kwargs):
            if not request.user.is_staff:
                raise Http404('You dontt have permission to do this. go away you hacker')
            return super().dispatch(request, *args, **kwargs)


class ContactDeleteView(LoginRequiredMixin, DeleteView):
    model = Contact
    success_url = reverse_lazy('crm:contact_list')
