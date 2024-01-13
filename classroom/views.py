from django.forms import ValidationError
from django.http import JsonResponse
from django.shortcuts import redirect 
from django.urls import reverse, reverse_lazy
from django.views.generic import DetailView, FormView, ListView, TemplateView

from classroom.api.api import *
from classroom.forms import ApprovedListForm, GroupForm
from classroom.models import Group, Lists
from classroom.services import (
    DeleteGroup,
    SetApprovedStudentsList,
    UpdateEnrolledStudentsList,
    UpdateMissingStudentsList,
)
from classroom.utils import (
    ApprovedStudentsListDoesNotExist,
    EnrolledStudentsListDoesNotExist,
    get_comparisons,
    is_ajax,
)

class ClassroomHomeView(TemplateView):
    # View que carrega a página inicial, que lista os cursos disponíveis
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        classroom_api = ClassroomAPI()
        courses = classroom_api.get_courses()
        context['courses'] = courses
         
        return context

class GroupCreateView(FormView):
    # View que carrega página para criação de novo grupo de turmas
    template_name = "group_create.html"
    form_class = GroupForm
    success_url = reverse_lazy("classroom:groups")

    def form_valid(self, form):
        self.object = form.save()
        group = self.object
        # group.save()

        return redirect(self.get_success_url()) 

class GroupListView(ListView):
    # View que carrega a lista de grupos
    template_name = "groups.html"
    model = Group

class ProcessDeleteGroupView(TemplateView):
    # View que processa o pedido de deleção de grupo e retorna uma
    # resposta json com o status do processo.
    def post(self, request, *args, **kwargs):
        if is_ajax(self.request):
            group_id = self.request.POST.get('group_id')

            service = DeleteGroup(group_id)
            try:
                service.execute()
            except:
                message = {'error': 'Não foi possível deletar este grupo.'}
            else:
                message = {'success': 'O grupo foi deletado com sucesso'}

            return JsonResponse(
                {'status': message,
                'redirect':reverse('classroom:groups')}
            )

class GroupDetailView(DetailView):
    # View que carrega a página de detalhes de um grupo de turmas
    template_name = "group_detail.html"
    model = Group

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        group = self.object 
        lists = Lists.objects.find_by_group_id(group.id)

        # Obtém quantidade de alunos matriculados no curso
        num_students = 0

        for student_group in lists.enrolled_list:
            num_students += len(student_group[1])

        context['num_students'] = num_students

        # Obtém formulário de lista de aprovados
        context['approved_form'] = ApprovedListForm()

        if lists:
            if lists.approved_list:
                context['approved_list'] = lists
                context['num_approved_list'] = len(lists.approved_list)
            else: context['approved_list'] = None

        return context

    def post(self, request, *args, **kwargs):
        if is_ajax(self.request):
            # Processa o pedido de atualização de lista de estudantes matriculados
            service = UpdateEnrolledStudentsList(self.kwargs['pk'])
            service.execute()
        else:
            # Processa a submissão da lista de alunos aprovados
            form = ApprovedListForm(data=request.POST, files=request.FILES)
            
            service = SetApprovedStudentsList(
                self.kwargs['pk'], 
                request.session,
                form
            )

            service.execute()

        return redirect(reverse_lazy("classroom:group", kwargs={'pk':kwargs['pk']}))

class ProcessSetApprovedStudentsListView(TemplateView):
    def post(self, request, *args, **kwargs):
        group_id = request.POST.get('group_id')
        form = ApprovedListForm(data=request.POST, files=request.FILES)
        
        service = SetApprovedStudentsList(
            group_id, 
            request.session,
            form
        )

        try:
            service.execute()
            return JsonResponse({'status': 'success'})
        except ValidationError as err:
            print(err.messages)
            return JsonResponse({'error':'Tipo de arquivo inválido. Tente fazer upload de um arquivo .csv.'})

class MissingStudentsView(DetailView):
    # View que carrega página de gerenciamento de lista de alunos faltantes
    template_name = "missing_students.html"
    model = Group

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lists = Lists.objects.find_by_group_id(self.kwargs['pk'])

        try:
            context['comparison_list'] = get_comparisons(lists)
        except EnrolledStudentsListDoesNotExist:
            context['enrolled_error'] = 'List of enrolled students have not been set yet. Please return and set it.'
        except ApprovedStudentsListDoesNotExist:
            context['approved_error'] = 'List of approved students have not been set yet. Please return and set it.'

        if lists.missing_list:
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
