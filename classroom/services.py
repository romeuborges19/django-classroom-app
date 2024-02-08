from django.forms import ValidationError
from classroom.api.api import GoogleAPI
from classroom.models import Group, Lists
from classroom.utils import get_missing_list

# Este arquivo contém a camada de serviços para o app classroom.
# Aqui, serão implementadas as lógicas necessárias para o funcionamento
# da aplicação.

class InvalidFileFormatError(Exception):
    pass

class SetApprovedStudentsList:
    # Classe de serviço que controla o processamento da definição da lista de alunos aprovados

    def __init__(self, group_id, session, form):
        self.form = form
        self.group = Group.objects.find(group_id)
        self.lists = Lists.objects.find_by_group_id(group_id)
        self.session_data = session

    def execute(self):
        try:
            if self.form.is_valid():
                if self.lists:
                    self.lists.delete()

                self.form.instance.group = self.group 
                self.form.save()
        except ValidationError:
            raise

class UpdateEnrolledStudentsList:
    # Classe de serviço que executa a operação de atualizar a lista 
    # de alunos matriculados

    def __init__(self, group_id):
        self.group = Group.objects.find(group_id)
        self.lists = Lists.objects.find_by_group_id(group_id)
        
        if not self.lists:
            self.lists = Lists.objects.create(group=self.group)

    def execute(self):
        self.lists.enrolled_list = self._get_students_list()
        self.group.students = self.lists.enrolled_list
        
        # Caso haja uma lista de alunos aprovados, a lista de alunos faltantes será atualizada.
        if self.lists.approved_list:
            if not self.lists.missing_list:
                self.lists.missing_list = get_missing_list(self.lists)

        self.lists.save()
        self.group.save()

    def _get_students_list(self):
        # Método que obtém, através da API do Google Classroom,
        # a lista de estudantes matriculados no curso 

        api = GoogleAPI();
        classes_info = api.get_course_data([value[0] for value in self.group.classes])
        students = []

        for i, course in enumerate(classes_info):
            students.append([self.group.classes[i][1], course['students']])

        return students

class UpdateMissingStudentsList:
    # Classe de serviço que controla a atualização da lista de alunos faltantes.

    def __init__(self, group_id, not_missing_list, missing_list):
        # Definindo o estado interno

        self.lists = Lists.objects.find_by_group_id(group_id)
        self.not_missing_list = not_missing_list
        self.missing_list = missing_list

    def execute(self):
        # Função principal da classe, que trata os dados e salva o 
        # objeto no banco de dados, que é renderizado na view

        self._clean_not_missing_list()
        self._clean_comparison_list()
        self.lists.save()

    def _clean_not_missing_list(self):
        # Tratando lista de alunos não faltantes
        for item in self.not_missing_list:
            item = item.split(',')
            for student in self.lists.missing_list:
                if student.get('fullname') == item[0]:
                    self.lists.missing_list.remove(student) 

    def _clean_comparison_list(self):
        # Removendo comparações que já foram feitas
        unknown_comparisons = []
        for item in self.missing_list:
            item = item.split(',')
            unknown_comparisons.append(item)
        if self.lists.unknown_list:
            for item in unknown_comparisons:
                self.lists.unknown_list.append(item)
        else:
            self.lists.unknown_list = unknown_comparisons

class DeleteGroup:
    # Classe de serviço que realiza a função de deletar um grupo e 
    # suas listas de estudantes correspondentes.
    def __init__(self, group_id):
        self.group = Group.objects.find(group_id)
        self.lists = Lists.objects.find_by_group_id(group_id)

    def execute(self):
        # Realiza a deleção das listas, do grupo e retorna o nome do grupo deletado.
        if self.lists:
            self.lists.delete()

        group_name = self.group.name
        self.group.delete()

        return group_name

class SendEmail:
    def __init__(self, subject, content, email_list=['romeuborges19@gmail.com']):
        self.email_list = email_list
        self.subject = subject
        self.content = content

    def execute(self):
        api = GoogleAPI()
        api.send_email(
            email_list=self.email_list,
            subject=self.subject,
            content=self.content
        )

        api.send_invitations(
            course_id='653538511313',
            receipt_list=self.email_list
        )
