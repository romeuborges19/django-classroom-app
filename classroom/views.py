from difflib import SequenceMatcher
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import DetailView, FormView, ListView, TemplateView
from oauthlib.oauth2 import MissingTokenError
from classroom.api.api import *
from classroom.forms import ApprovedListForm, GroupForm
from classroom.models import ApprovedList, Group
from classroom.utils import get_comparisons, get_missing_students_list, is_ajax

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
            lists = ApprovedList.objects.filter(group_id=kwargs['pk']).first()
            api = GCApi();
            classes_info = api.get_course_data([value[0] for value in group.classes])
            students = []

            for i, course in enumerate(classes_info):
                students.append([group.classes[i][1], course['students']])

            lists.enrolled_list = students
            lists.missing_list = get_missing_students_list(lists)
            lists.save()
        else:
            # Processa a submissão da lista de alunos aprovados

            approved_list_form = ApprovedListForm(request.POST, request.FILES)
            approved_list = ApprovedList.objects.filter(group_id=kwargs['pk']).first()

            if approved_list_form.is_valid():
                if request.session.has_key('form_error'):
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

        lists = ApprovedList.objects.filter(group_id=self.kwargs['pk']).first()

        context['comparison_list'] = get_comparisons(lists)

        context['missing_list'] = lists.missing_list
        context['num_missing_list'] = len(lists.missing_list)


        return context

    def post(self, request, *args, **kwargs):
        if is_ajax(self.request):
            not_missing_list = self.request.POST.getlist('not_missing_list[]')
            missing_list = self.request.POST.getlist('missing_list[]')
            lists = ApprovedList.objects.filter(group_id=kwargs['pk']).first()

            # Tratando lista de alunos não faltantes
            for item in not_missing_list:
                item = item.split(',')

                for student in lists.missing_list:
                    if student.get('fullname') == item[0]:
                        lists.missing_list.remove(student) 
                        print(f'{student} removed')

            unknown_comparisons = []
            for item in missing_list:
                item = item.split(',')

                unknown_comparisons.append(item)

            print(unknown_comparisons)
            if lists.unknown_list:
                for item in unknown_comparisons:
                    lists.unknown_list.append(item)
            else:
                lists.unknown_list = unknown_comparisons

            print(lists.unknown_list)

            lists.save()

            return redirect(reverse_lazy("classroom:group", kwargs={'pk':kwargs['pk']}))
        else:
            missing_list = self.request.POST.get('missing_list')
