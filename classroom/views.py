from difflib import SequenceMatcher
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import DetailView, FormView, ListView, TemplateView
from oauthlib.oauth2 import MissingTokenError
from classroom.api.api import *
from classroom.forms import ApprovedListForm, GroupForm
from classroom.models import Group, Lists
from classroom.services import InvalidFileFormatError, SetApprovedStudentsList, UpdateEnrolledStudentsList, UpdateMissingStudentsList
from classroom.utils import get_comparisons, get_missing_list, is_ajax

class ClassroomHomeView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        api = GCApi()
        courses = api.get_courses()
        context['courses'] = courses

        api.call_gmail()
         
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

        approved_list = Lists.objects.filter(group=group).first()

        if approved_list:
            context['approved_list'] = approved_list
            context['num_approved_list'] = len(approved_list.approved_list)
        else: context['approved_list'] = None

        if self.request.session.has_key('form_error'):
            context['form_error'] = self.request.session['form_error']

        return context

    def post(self, request, *args, **kwargs):
        if is_ajax(self.request):
            # Processa o pedido de atualização de lista de estudantes matriculados
            service = UpdateEnrolledStudentsList(self.kwargs['pk'])
            service.execute()

        else:
            # Processa a submissão da lista de alunos aprovados

            approved_list_form = ApprovedListForm(request.POST, request.FILES)
            
            service = SetApprovedStudentsList(
                self.kwargs['pk'], 
                request.session,
                approved_list_form
            )

            try:
                service.execute()
            except InvalidFileFormatError:
                request.session['form_error'] = "Invalid file format. Try uploading a .csv file."

        return redirect(reverse_lazy("classroom:group", kwargs={'pk':kwargs['pk']}))

class MissingStudentsView(DetailView):
    template_name = "missing_students.html"
    model = Group

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lists = Lists.objects.find_by_group_id(self.kwargs['pk'])

        context['comparison_list'] = get_comparisons(lists)
        context['missing_list'] = lists.missing_list
        context['num_missing_list'] = len(lists.missing_list)

        return context

    def post(self, request, *args, **kwargs):
        if is_ajax(self.request):

            service = UpdateMissingStudentsList(
                kwargs['pk'],
                self.request.POST.getlist('not_missing_list[]'),
                self.request.POST.getlist('missing_list[]')
            )

            service.execute()

            return redirect(reverse_lazy("classroom:group", kwargs={'pk':kwargs['pk']}))
