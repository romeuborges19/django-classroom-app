from django.shortcuts import render
from django.views.generic import TemplateView
from classroom.api.api import *

# Create your views here.

class ClassroomView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        api = GCApi()
        courses = api.get_courses()
        context['courses'] = courses
         
        return context

class ClassroomGroupCreateView(TemplateView):
    template_name = "create_group.html"
