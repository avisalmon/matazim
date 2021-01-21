from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.http import Http404
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView, CreateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from .models import Camp, MasterStage, Stage, \
                    MasterTask, Task, MasterItem, Item, \
                    MasterCollateral, Collateral
# from .forms import ProjectForm, PicForm, LinkForm

# **** Camp ****

class CampListView(LoginRequiredMixin, ListView):
    model = Camp

    def get_context_data(self, **kwargs):
        context = super(CampListView, self).get_context_data(**kwargs)
        try:
            master_stages = MasterStage.objects.all()
            context['master_stages'] = master_stages
            print(master_stages)
        except:
            pass

        # except Registration.DoesNotExist:
        #     registration = None

        return context


class CampCreateView(LoginRequiredMixin, CreateView):
    model=Camp
    fields = ['title', 'departement', 'participating_num']

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.owner = self.request.user
        obj.save()

        # populate Campaign here
        try:
            master_stages = MasterStage.objects.all()
            # Create stages
            for master_stage in master_stages:
                stage = Stage.objects.create(
                    title=master_stage.title,
                    description=master_stage.description,
                    reference=master_stage,
                    camp=obj,
                    )
                # create tasks
                master_tasks = MasterTask.objects.filter(master_stage=master_stage)
                for master_task in master_tasks:
                    task = Task.objects.create(title=master_task.title,
                                               description=master_task.description,
                                               reference=master_task,
                                               stage=stage,
                                               )
                    # create items
                    master_items = MasterItem.objects.filter(master_task=master_task)
                    for master_item in master_items:
                        item = Item.objects.create(title=master_item.title,
                                                   reference=master_item,
                                                   task=task,
                                                   )
                        # create collaterals
                        master_collaterals = MasterCollateral.objects.filter(master_item=master_item)
                        for master_collateral in master_collaterals:
                            collateral = Collateral.objects.create(description=master_collateral.description,
                                                                   item=item,
                                                                   reference=master_collateral,
                                                                   collateral_type=master_collateral.collateral_type,
                                                                   )

        except:
            pass


        return super().form_valid(form)


class CampDetailView(LoginRequiredMixin, DetailView):
    model = Camp


class  CampUpdateView(LoginRequiredMixin, UpdateView):
    model = Camp
    fields = ['title', 'departement', 'participating_num']

    # making sure only the owner can update
    def get_object(self):
        camp = super(CampUpdateView, self).get_object()
        if not camp.owner == self.request.user:
            raise Http404('You dontt have permission to do this. go away you hacker')
        return camp

# *** Stage ****

class StageUpdateView(LoginRequiredMixin, UpdateView):
    model=Stage
    fields = ['title', 'description', 'start_ww', 'end_ww']

    def get_success_url(self):
        return reverse('funnel:camp_detail', kwargs={'pk': self.object.camp.pk })

    def get_object(self):
        stage = super(StageUpdateView, self).get_object()
        if not stage.camp.owner == self.request.user:
            raise Http404('You dontt have permission to do this. go away you hacker')
        return stage

# *** Tasks ****

# Create
class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    fields = ['title', 'description']

    def form_valid(self, form):
        obj = form.save(commit=False)
        stage = get_object_or_404(Stage, pk=self.kwargs['stage_pk'])
        obj.stage = stage
        if not stage.camp.owner == self.request.user:
            raise Http404('You dontt have permission to do this. go away you hacker')
        obj.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('funnel:camp_detail', kwargs={'pk': self.object.stage.camp.pk })

# Update
class TaskUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    fields = ['title', 'description']

    # here you can make your custom validation for any particular user
    def dispatch(self, request, *args, **kwargs):
            task = get_object_or_404(Task, pk=kwargs['pk'])
            if request.user != task.stage.camp.owner:
                raise Http404('You dontt have permission to do this. go away you hacker')
            return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('funnel:camp_detail', kwargs={'pk': self.object.stage.camp.pk })

# DELETE
class TaskDeleteView(LoginRequiredMixin, DeleteView):
    model = Task

    def dispatch(self, request, *args, **kwargs):
            task = get_object_or_404(Task, pk=kwargs['pk'])
            if request.user != task.stage.camp.owner:
                raise Http404('You dontt have permission to do this. go away you hacker')
            return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('funnel:camp_detail', kwargs={'pk': self.object.stage.camp.pk })

# **** Items ******
#CrUD

class ItemCreateView(LoginRequiredMixin, CreateView):
    model = Item
    fields = ['title']

    def form_valid(self, form):
        obj = form.save(commit=False)
        task = get_object_or_404(Task, pk=self.kwargs['task_pk'])
        obj.task = task
        if not task.stage.camp.owner == self.request.user:
            raise Http404('You dontt have permission to do this. go away you hacker')
        obj.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('funnel:camp_detail', kwargs={'pk': self.object.task.stage.camp.pk })


class ItemUpdateView(LoginRequiredMixin, UpdateView):
    model = Item
    fields = ['title']

    def dispatch(self, request, *args, **kwargs):
            item = get_object_or_404(Item, pk=kwargs['pk'])
            if request.user != item.task.stage.camp.owner:
                raise Http404('You dontt have permission to do this. go away you hacker')
            return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('funnel:camp_detail', kwargs={'pk': self.object.task.stage.camp.pk })


class ItemDeleteView(LoginRequiredMixin, DeleteView):
    model = Item

    def dispatch(self, request, *args, **kwargs):
            item = get_object_or_404(Item, pk=kwargs['pk'])
            if request.user != item.task.stage.camp.owner:
                raise Http404('You dontt have permission to do this. go away you hacker')
            return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('funnel:camp_detail', kwargs={'pk': self.object.task.stage.camp.pk })


def item_complete(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if item.task.stage.camp.owner == request.user:
        item.complete()
    item.save()
    return redirect('funnel:camp_detail', pk=item.task.stage.camp.pk)


def item_decomplete(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if item.task.stage.camp.owner == request.user:
        item.decomplete()
    item.save()
    return redirect('funnel:camp_detail', pk=item.task.stage.camp.pk)


# ***** Collaterals ******
class CollateralAddImage(LoginRequiredMixin, CreateView):
    model = Collateral
    fields = ['description', 'image']
    template_name = 'funnel/image_form.html'

    def form_valid(self, form):
        obj = form.save(commit=False)
        item = get_object_or_404(Item, pk=self.kwargs['item_pk'])
        obj.item = item
        obj.collateral_type = 'IM'
        if not item.task.stage.camp.owner == self.request.user:
            raise Http404('You dontt have permission to do this.')
        obj.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('funnel:camp_detail',
                        kwargs={'pk': self.object.item.task.stage.camp.pk })


class CollateralAddFile(LoginRequiredMixin, CreateView):
    model = Collateral
    fields = ['description', 'file']
    template_name = 'funnel/file_form.html'

    def form_valid(self, form):
        obj = form.save(commit=False)
        item = get_object_or_404(Item, pk=self.kwargs['item_pk'])
        obj.item = item
        obj.collateral_type = 'FI'
        if not item.task.stage.camp.owner == self.request.user:
            raise Http404('You dontt have permission to do this.')
        obj.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('funnel:camp_detail',
                        kwargs={'pk': self.object.item.task.stage.camp.pk })


class CollateralAddLink(LoginRequiredMixin, CreateView):
    model = Collateral
    fields = ['description', 'url']
    template_name = 'funnel/link_form.html'

    def form_valid(self, form):
        obj = form.save(commit=False)
        item = get_object_or_404(Item, pk=self.kwargs['item_pk'])
        obj.item = item
        obj.collateral_type = 'LI'
        if not item.task.stage.camp.owner == self.request.user:
            raise Http404('You dontt have permission to do this.')
        obj.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('funnel:camp_detail',
                        kwargs={'pk': self.object.item.task.stage.camp.pk })


class CollateralUpdateImage(LoginRequiredMixin, UpdateView):
    model = Collateral
    fields = ['description', 'image']
    template_name = 'funnel/image_form.html'

    def get_object(self):
        collateral = super(CollateralUpdateImage, self).get_object()
        if not collateral.item.task.stage.camp.owner == self.request.user:
            raise Http404('You dontt have permission to do this. go away you hacker')
        return collateral

    def get_success_url(self):
        return reverse('funnel:camp_detail',
                        kwargs={'pk': self.object.item.task.stage.camp.pk })


class CollateralUpdateFile(LoginRequiredMixin, UpdateView):
    model = Collateral
    fields = ['description', 'file']
    template_name = 'funnel/file_form.html'

    def get_object(self):
        collateral = super(CollateralUpdateFile, self).get_object()
        if not collateral.item.task.stage.camp.owner == self.request.user:
            raise Http404('You dontt have permission to do this. go away you hacker')
        return collateral

    def get_success_url(self):
        return reverse('funnel:camp_detail',
                        kwargs={'pk': self.object.item.task.stage.camp.pk })


class CollateralUpdateLink(LoginRequiredMixin, UpdateView):
    model = Collateral
    fields = ['description', 'url']
    template_name = 'funnel/image_form.html'

    def get_object(self):
        collateral = super(CollateralUpdateLink, self).get_object()
        if not collateral.item.task.stage.camp.owner == self.request.user:
            raise Http404('You dontt have permission to do this. go away you hacker')
        return collateral

    def get_success_url(self):
        return reverse('funnel:camp_detail',
                        kwargs={'pk': self.object.item.task.stage.camp.pk })


class CollateralDeleteView(LoginRequiredMixin, DeleteView):
    model = Collateral

    def dispatch(self, request, *args, **kwargs):
            collateral = get_object_or_404(Collateral, pk=kwargs['pk'])
            if request.user != collateral.item.task.stage.camp.owner:
                raise Http404('You dontt have permission to do this. go away you hacker')
            return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('funnel:camp_detail', kwargs={'pk': self.object.item.task.stage.camp.pk })
