import json
from django.forms import ValidationError
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    DetailView,
    FormView,
    ListView,
    TemplateView,
    UpdateView,
)
from django.views.generic.edit import FormMixin

from classroom.api.api import *
from classroom.forms import (
    ApprovedListCSVForm,
    ApprovedListGoogleFormsForm,
    EmailMessageForm,
    GroupForm,
    UpdateGroupForm,
)
from classroom.models import Group, Lists, Message
from classroom.services import (
    DeleteGroup,
    SendEmail,
    SetApprovedListFromCSV,
    SetApprovedListFromForms,
    UpdateEnrolledStudentsList,
    UpdateMissingStudentsList,
)
from classroom.utils import get_comparisons, is_ajax

class ClassroomHomeView(TemplateView):
    # View que carrega a página inicial, que lista os cursos disponíveis
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        api = GoogleAPI()
        courses = api.get_courses()
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
        
        service = SetApprovedListFromForms(
            group=group,
            associated_form_id=group.associated_form_id
        )
        service.execute()

        service = UpdateEnrolledStudentsList(group.id)
        service.execute()
        group.save()

        return redirect(self.get_success_url()) 

class GroupUpdateView(UpdateView):
    template_name = "group_update.html"
    model = Group
    form_class = UpdateGroupForm
    success_url = reverse_lazy("classroom:groups")

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

        # Obtém formulário de lista de aprovados
        context['approved_form_csv'] = ApprovedListCSVForm()
        context['approved_form_gforms'] = ApprovedListGoogleFormsForm()

        email_success_message = self.request.session.get('email_success')
        if email_success_message:
            context['email_success'] = email_success_message
            del self.request.session['email_success']

        email_error_message = self.request.session.get('email_error')
        if email_error_message:
            context['email_error'] = email_error_message
            del self.request.session['email_error']

        form_error_message = self.request.session.get('form_error')
        if form_error_message:
            context['form_error'] = form_error_message
            del self.request.session['form_error']

        # Obtém quantidade de alunos matriculados no curso
        if lists:
            num_students = 0

            if lists.enrolled_list:
                for student_group in lists.enrolled_list:
                    num_students += len(student_group[1])

            context['num_students'] = num_students

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

        return redirect(reverse_lazy("classroom:group", kwargs={'pk':kwargs['pk']}))

class ProcessSetApprovedStudentsListView(TemplateView):
    template_name = 'teste.html'
    def post(self, request, *args, **kwargs):
        group_id = request.POST.get('groupId')
        form = ApprovedListCSVForm(data=request.POST, files=request.FILES)
        
        service = SetApprovedListFromCSV(
            group_id, 
            form
        )

        try:
            service.execute()
            return JsonResponse({'status': 'Lista definida com sucesso.'})
        except ValidationError as err:
            return JsonResponse({'error':f'{err.messages[0]}'})

class ProcessSetApprovedStudentsListFromFormsView(TemplateView):
    template_name = 'teste.html'
    def post(self, request, *args, **kwargs):
        group_id = request.POST.get('groupId')
        group = Group.objects.find(group_id)
        associated_form_id = request.POST.get('associated_form')

        service = SetApprovedListFromForms(
            group=group,
            associated_form_id=associated_form_id
        )
        try:
            service.execute()
            return JsonResponse({'status': 'Lista definida com sucesso.'})
        except ValidationError as err:
            return JsonResponse({'error': f'{err.messages[0]}'})

        

class MissingStudentsView(DetailView):
    # View que carrega página de gerenciamento de lista de alunos faltantes
    template_name = "missing_students.html"
    model = Group

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lists = Lists.objects.find_by_group_id(self.kwargs['pk'])

        try:
            context['comparison_list'] = get_comparisons(lists)
        except Exception as err:
            context['lists_error'] = err 



        if lists:
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

class EmailStudentsView(FormMixin, DetailView):
    model = Group
    template_name = 'email_students.html'
    form_class = EmailMessageForm

class SendInvitationsView(DetailView):
    model = Group
    template_name = 'teste.html'

    def post(self, request, *args, **kwargs):
        recipient = self.request.POST.get('recipient')
        subject = self.request.POST.get('subject')
        content = self.request.POST.get('content')

        try:
            service = SendEmail(
                group_id=kwargs['pk'],
                recipient=recipient,
                subject=subject,
                content=content
            )     

            service.execute()
        except Exception as err:
            self.request.session['email_error'] = f"Impossível enviar e-mail: {err}"
        else:

            self.request.session['email_success'] = "E-mail enviado com sucesso."

        return redirect(reverse_lazy('classroom:group', kwargs={'pk':kwargs['pk']}))

class EmailMessagesView(ListView):
    template_name = 'message_list.html'

    def get_queryset(self):
        queryset = Message.objects.list_by_group(self.kwargs['pk'])

        return queryset 

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs) 
        context['group_id'] = self.kwargs['pk']

        return context

class AssociateForm(DetailView):
    model = Group
    template_name = 'associate_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        api = GoogleAPI() 
        forms = api.get_forms()
        context['forms'] = forms
        return context
