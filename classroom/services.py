from django.forms import ValidationError

from classroom.api.api import GoogleAPI
from classroom.models import Group, Lists, Message
from classroom.utils import (
    ApprovedStudentsListDoesNotExist,
    EnrolledStudentsListDoesNotExist,
    ListsDoesNotExist,
    MissingStudentListDoesNotExist,
    get_missing_list,
)

# Este arquivo contém a camada de serviços para o app classroom.
# Aqui, serão implementadas as lógicas necessárias para o funcionamento
# da aplicação.

class InvalidFileFormatError(Exception):
    pass

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
    # Classe de serviço que envia e-mail à lista de destinatários especificada
    # e armazena este e-mail no banco de dados
    def __init__(self, group_id, recipient, subject, content):
        self.group_id = group_id
        self.recipient = recipient
        self.subject = subject
        self.content = content

    def execute(self):
        api = GoogleAPI()
        email_list = self._get_email_list()
        # !!! CÓDIGO COMENTADO POR QUESTÕES DE SEGURANÇA NO DESENVOLVIMENTO
        api.send_email(
            email_list=email_list,
            subject=self.subject,
            content=self.content
        )

        # if self.recipient == "faltantes":
        #     api.send_invitations(
        #         course_id='653538511313',
        #         receipt_list=email_list
        #     )

        self._save_message()

    def _save_message(self):
        group = Group.objects.find(self.group_id)
        Message.objects.create(
            recipient=self.recipient,
            subject=self.subject,
            content=self.content,
            group=group
        )

    def _get_email_list(self):
        lists = Lists.objects.find_by_group_id(self.group_id)
        if not lists:
            raise ListsDoesNotExist("Listas associadas ao grupo não foram definidas")

        email_list = []
        if self.recipient == "matriculados":
            if lists.enrolled_list:
                for course in lists.enrolled_list:
                    for student in course[1]:
                        email_list.append(student['email'])
            else:
                raise EnrolledStudentsListDoesNotExist("Lista de estudantes matriculados não registrada.")

        if self.recipient == "faltantes":
            if lists.missing_list:
                for course in lists.missing_list:
                    for student in course[1]:
                        email_list.append(student['email'])
            else:
                raise MissingStudentListDoesNotExist("Lista de estudantes faltantes não registrada.")

        if self.recipient == "aprovados":
            if lists.approved_list:
                for course in lists.approved_list:
                    for student in course[1]:
                        email_list.append(student['email'])
            else:
                raise ApprovedStudentsListDoesNotExist("Lista de estudantes aprovados não registrada.")

        return email_list

class SetApprovedListFromForms:
    # Classe de serviço que define lista de alunos aprovados a partir de respostas
    # de formulário do Google Forms
    def __init__(self, group, associated_form_id): 
        self.group = group
        self.associated_form_id = associated_form_id

    def execute(self):
        api = GoogleAPI()
    
        if self._valid_form_id:
            lists = Lists.objects.find_by_group_id(group_id=self.group.pk)
            if not lists:
                lists = Lists.objects.create(group=self.group)

            try:
                _, email_qid, name_qid = api.get_form(self.associated_form_id)
            except Exception as err:
                raise err

            approved_list = api.get_approved_list_from_form(
                form_id=self.associated_form_id,
                email_qid=email_qid,
                name_qid=name_qid
            )

            lists.approved_list = approved_list
            lists.save()
            return len(approved_list)
        

    def _valid_form_id(self):
        if self.associated_form_id == "0":
            return False
        return True

class SetApprovedListFromCSV:
    # Classe de serviço que controla o processamento da definição da lista de alunos aprovados
    def __init__(self, group_id, form):
        self.form = form
        self.group = Group.objects.find(group_id)
        self.lists = Lists.objects.find_by_group_id(group_id)

    def execute(self):
        if self.form.is_valid():
            if self.lists:
                self.lists.delete()

            self.form.instance.group = self.group 
            self.form.save()
        else:
            for error in self.form.non_field_errors():
                raise ValidationError(f'{error}')

