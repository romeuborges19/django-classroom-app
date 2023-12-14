from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import DetailView, FormView, ListView, TemplateView
from classroom.api.api import *
from classroom.forms import ApprovedListForm, GroupForm
from classroom.models import ApprovedList, Group

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        group = self.object 

        # Obtém quantidade de alunos matriculados no curso
        num_students = 0

        for student_group in group.students:
            num_students += len(student_group[1])

        context['num_students'] = num_students
        context['approved_form'] = ApprovedListForm()

        approved_list = ApprovedList.objects.filter(group=group).first()

        if approved_list:
            context['approved_list'] = approved_list
            context['num_approved_list'] = len(approved_list.approved_list)
        else: context['approved_list'] = None

        return context

    def post(self, request, *args, **kwargs):
        approved_list_form = ApprovedListForm(request.POST)

        approved_list = ApprovedList.objects.filter(group_id=kwargs['pk']).first()

        if approved_list_form.is_valid():
            if approved_list:
                approved_list.delete()
            approved_list_form.instance.group = Group.objects.filter(id=kwargs['pk']).first()
            approved_list_form.save()

        return redirect(reverse_lazy("classroom:group", kwargs={'pk':kwargs['pk']}))
