from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import DetailView, FormView, ListView, TemplateView
from classroom.api.api import *
from classroom.forms import GroupForm
from classroom.models import Group

class ClassroomHomeView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        api = GCApi()
        courses = api.get_courses()
        context['courses'] = courses
         
        return context

class GroupCreateView(FormView):
    template_name = "group_create.html"
    form_class = GroupForm
    success_url = reverse_lazy("classroom:groups")

    def form_valid(self, form):
        print('form valid')
        self.object = form.save()
        group = self.object
        group.save()

        return redirect(self.get_success_url()) 

class GroupListView(ListView):
    template_name = "groups.html"
    model = Group

class GroupDetailView(DetailView):
    template_name = "group_detail.html"
    model = Group

