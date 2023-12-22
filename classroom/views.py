from difflib import SequenceMatcher
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import DetailView, FormView, ListView, TemplateView
from oauthlib.oauth2 import MissingTokenError
from classroom.api.api import *
from classroom.forms import ApprovedListForm, GroupForm
from classroom.models import ApprovedList, Group
from classroom.utils import is_ajax

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

        # Obtém formulário de lista de aprovados
        context['approved_form'] = ApprovedListForm()

        approved_list = ApprovedList.objects.filter(group=group).first()

        if approved_list:
            context['approved_list'] = approved_list
            context['num_approved_list'] = len(approved_list.approved_list)
        else: context['approved_list'] = None

        return context

    def post(self, request, *args, **kwargs):
        if is_ajax(self.request):
            # Processa o pedido de atualização de lista de estudantes matriculados

            group = Group.objects.filter(id=kwargs['pk']).first()
            api = GCApi();
            classes_info = api.get_course_data([value[0] for value in group.classes])
            students = []

            for i, course in enumerate(classes_info):
                students.append([group.classes[i][1], course['students']])

            group.students = students
            group.save()
        else:
            # Processa a submissão da lista de alunos aprovados

            approved_list_form = ApprovedListForm(request.POST, request.FILES)
            approved_list = ApprovedList.objects.filter(group_id=kwargs['pk']).first()

            if approved_list_form.is_valid():
                del request.session['form_error']

                if approved_list:
                    approved_list.delete()

                approved_list_form.instance.group = Group.objects.filter(id=kwargs['pk']).first()
                approved_list_form.save()
            else:
                request.session['form_error'] = approved_list_form.errors

        return redirect(reverse_lazy("classroom:group", kwargs={'pk':kwargs['pk']}))



class MissingStudentsView(DetailView):
    template_name = "missing_students.html"
    model = Group

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        group = self.object
        approved_list = ApprovedList.objects.filter(group_id=self.object.id).first()
        approved_list = approved_list.approved_list
        context['approved_list'] = approved_list
        missing_list = []
        students_emails = []
        students_fullnames = []

        for student_group in group.students:
            for student in student_group[1]:
                students_emails.append(student['email'])
                students_fullnames.append(student['fullname'].lower())

        for approved_student in approved_list:
            if approved_student['email'] not in students_emails:
                missing_list.append(approved_student)

        # Obtém lista de nomes semelhantes para comparação
        comparison_list = []

        for missing_student in missing_list:
            next = False
            missing_name = missing_student['fullname'].lower()
            for fullname in students_fullnames:
                fullname = fullname.lower()
                missing_name_split = missing_name.split(' ')
                fullname_split = fullname.split(' ')
                if missing_name_split[0] == fullname_split[0]:
                    similarity = similar(missing_name, fullname)
                    if similarity > 0.4:
                        comparison_list.append([missing_name, fullname])
                        next = True
                        break
                if next: 
                    break

        
        context['comparison_list'] = comparison_list
        context['missing_list'] = missing_list 
        context['num_missing_list'] = len(missing_list)

        return context

    def post(self, request, *args, **kwargs):
        if is_ajax(self.request):
            print(self.request.POST.get('not_missing_list'))


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()
