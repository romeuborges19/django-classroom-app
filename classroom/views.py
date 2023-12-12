from django.shortcuts import render
from django.views.generic import TemplateView
from classroom.api.quickstart import *

# Create your views here.

class ClassroomView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        courses = get_courses()
        print(courses)

        context['courses'] = courses
         
        return context
