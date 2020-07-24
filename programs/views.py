from django.shortcuts import render, reverse, redirect
from django.urls import reverse_lazy
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from .models import Program, Facilitator, Facility
from main.models import Profile


# def matazim_main(request):
#     return render(request, 'matazim/main_matazim.html')


class ProgramListView(ListView):
    model=Program


class ProgramDetailView(DetailView):
    model=Program


class ProgramCreateView(LoginRequiredMixin, CreateView):
    model=Program
    fields = ['name', 'description', 'link', 'image']

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.owner = self.request.user
        obj.save()
        return super().form_valid(form)


class ProgramUpdateView(LoginRequiredMixin, UpdateView):
    model=Program
    fields = ['name', 'description', 'link', 'image']

    def dispatch(self, request, *args, **kwargs):
        """" Making sure that only owners can update """
        obj = self.get_object()
        print(f'obj: {obj}')
        if obj.owner != self.request.user:
            print('Hi')
            return redirect('programs:program_list')
        return super(ProgramUpdateView, self).dispatch(request, *args, **kwargs)


class ProgramDeleteView(DeleteView):
    model=Program
    success_url = reverse_lazy('programs:program_list')

## Addint a school to a program
class ProgramAddSchoolList(ListView):
    model=Facilitator
    template_name = 'programs/program_add_school.html'
    context_object_name = 'facilitators'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(ProgramAddSchoolList, self).get_context_data(**kwargs)
        # Add stuff
        program = Program.objects.get(pk=self.kwargs['source_program'])
        context['source_program'] = self.kwargs['source_program']
        context['program'] = program
        return context

def program_add_school_action(request, source_program, dest_facilitator):
    program = Program.objects.get(pk=source_program)
    facilitator = Facilitator.objects.get(pk=dest_facilitator)
    facilitator.programs.add(program)
    return redirect(program)

def program_delet_school_action(request, source_program, dest_facilitator):
    program = Program.objects.get(pk=source_program)
    facilitator = Facilitator.objects.get(pk=dest_facilitator)
    facilitator.programs.remove(program)
    return redirect(program)

## End of adding a school to a program

def program_add_member(request, program_id, profile_id):
    try:
        program = Program.objects.get(pk=program_id)
        profile = Profile.objects.get(pk=profile_id)
    except:
        return redirect('programs:program_list')

    program.members.add(profile)
    return redirect('programs:program_detail', pk=program_id)

def program_remove_member(request, program_id, profile_id):
    print(f'got here with {program_id} and {profile_id}')
    try:
        program = Program.objects.get(pk=program_id)
        profile = Profile.objects.get(pk=profile_id)
    except:
        return redirect('programs:program_list')

    program.members.remove(profile)
    return redirect('programs:program_detail', pk=program_id)

## ***************** Facilitator *********************

class FacilitatorListView(ListView):
    model=Facilitator


class FacilitatorDetailView(DetailView):
    model=Facilitator


class FacilitatorCreateView(LoginRequiredMixin, CreateView):
    model=Facilitator
    fields = ['name', 'description', 'link', 'image']

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.owner = self.request.user
        obj.save()
        return super().form_valid(form)


class FacilitatorUpdateView(LoginRequiredMixin, UpdateView):
    model=Facilitator
    fields = ['name', 'description', 'link', 'image']

    def dispatch(self, request, *args, **kwargs):
        """" Making sure that only owners can update """
        obj = self.get_object()
        if obj.owner != self.request.user:
            return redirect('programs:facilitator_list')
        return super(FacilitatorUpdateView, self).dispatch(request, *args, **kwargs)


class FacilitatorDeleteView(DeleteView):
    model=Facilitator
    success_url = reverse_lazy('programs:facilitator_list')


def facilitator_add_member(request, facilitator_id, profile_id):
    print(f'got in. facilitator {facilitator_id}, profile {profile_id}')
    try:
        facilitator = Facilitator.objects.get(pk=facilitator_id)
        profile = Profile.objects.get(pk=profile_id)
    except:
        return redirect('programs:facilitator_list')

    facilitator.members.add(profile)
    return redirect('programs:facilitator_detail', pk=facilitator_id)

def facilitator_remove_member(request, facilitator_id, profile_id):
    try:
        facilitator = Facilitator.objects.get(pk=facilitator_id)
        profile = Profile.objects.get(pk=profile_id)
    except:
        return redirect('programs:facilitator_list')

    facilitator.members.remove(profile)
    return redirect('programs:facilitator_detail', pk=facilitator_id)
