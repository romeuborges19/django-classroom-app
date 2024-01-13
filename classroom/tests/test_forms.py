from io import StringIO
from django.test import RequestFactory, TestCase
from django.urls import reverse

from classroom.models import Group, Lists


class ApprovedStudentsListFormTest(TestCase):
    def setUp(self):
        classes = [["590861439156", "Introdução à Biblioteca Pandas - Python"]]
        students = [["Introdução à Biblioteca Pandas - Python", [
            {"id": 1, "email": "hemmerson.rosa@estudante.ifto.edu.br", "fullname": "Hemmerson Luis Barros da Rosa"}, 
            {"id": 2, "email": "denise.maranhao@estudante.ifto.edu.br", "fullname": "DENISE VIEIRA MARANHÃO"}, 
            {"id": 3, "email": "luiz.jupiter@mail.uft.edu.br", "fullname": "Luiz Jupiter Carneiro de Souza"}
        ]]]
        self.factory = RequestFactory()
        self.group = Group.objects.create(
            name="test_group",
            classes=classes,
            students=students
        )
        self.lists = Lists.objects.create(
            enrolled_list=[
                ["Inteligência Artificial com foco em Sistemas de Recomendação (Turma 1-C)", [
                    {"id": 1, "email": "arqlucasdantas@gmail.com", "fullname": "Lucas Dantas"}, 
                    {"id": 2, "email": "joaovitoralves163@gmail.com", "fullname": "I am Jhon (Joãozito)"}, 
                    {"id": 3, "email": "moiseslopesti2022@gmail.com", "fullname": "moises lopes soares"}]]],
            missing_list=[
                {"email": "rafael.mansilha@gmail.com", "fullname": "rafael mansilha murta"}, 
                {"email": "jr.luizandrade@gmail.com", "fullname": "luiz lopes de andrade júnior"}, 
                {"email": "lopesnewton8@gmail.com", "fullname": "newton lopes de figueiredo neto"}],
            unknown_list=[
                ["rafael mansilha murta", "rafael freitas", "rafael.afmendonca1994@gmail.com"],
                ["rafael mansilha murta", "rafael de brito albuquerque", "rba0606@gmail.com"],
                ["luiz lopes de andrade júnior", "luiz carvalho", "maximusmano@gmail.com"]],
            group=self.group
        )

        self.csv_file_content =[['fullname', 'email'], 
                                ['Gabriel Reis Nadler Prata','gabrielreisnp@gmail.com'],
                                ['Rafael Mansilha Murta','rafael.mansilha@gmail.com'],
                                ['Eduardo de Sá Coêlho Ribeiro Costa','eduardodesacoelho08@gmail.com']]

        self.csv_file = StringIO("""\
fullname,email
Gabriel Reis Nadler Prata,gabrielreisnp@gmail.com
Rafael Mansilha Murta,rafael.mansilha@gmail.com
Eduardo de Sá Coêlho Ribeiro Costa,eduardodesacoelho08@gmail.com""")

        self.csv_file.name = 'test_file.csv'




    def test_approved_students_list_is_set_correctly(self):
        # Testa se o processo de definição de lista de estudantes aprovados
        # está sendo realizado corretamente

        response = self.client.post(reverse(
            'classroom:group',
            kwargs={'pk': self.group.pk}
        ), {'approved_list_csv': self.csv_file}, follow=True) 

        self.assertTrue(not response.context.get('form_error'))

    def test_approved_students_list_being_set_with_wrong_file_type(self):
        # Testa se está sendo retornada uma mensagem de erro
        self.csv_file.name = 'test_file.txt'

        response = self.client.post(reverse(
            'classroom:group',
            kwargs={'pk': self.group.pk}
        ), {'approved_list_csv': self.csv_file}, follow=True) 

        self.assertTrue(response.context.get('form_error'))

class CreateGroupFormTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.form_data = {
            'name':'test_group',
            'avaliable_classes': ["('590861439156', 'Curso de exploração de dados com Pandas - Python')"]
        }

    def test_create_group_form_is_valid_with_valid_data(self):
        # Testa se o formulário é válido com entradas válidas
        form = GroupForm(data=self.form_data)

        self.assertTrue(form.is_valid())

    def test_create_group_form_is_valid_with_blank_data(self):
        # Testa se o formulário é válido com entradas em branco. 
        # Espera-se que form.is_valid() retorne False.
        self.form_data['name'] = ''
        self.form_data['avaliable_classes'] = ''
        form = GroupForm(data=self.form_data)

        self.assertTrue(not form.is_valid())

    def test_create_group_form_is_valid_without_selecting_classes(self):
        # Testa se o formulário é válido sem que o usuário escolha as turmas do grupo.
        # Espera-se que form.is_valid() retorne False.
        self.form_data['name'] = 'test_group'
        self.form_data['avaliable_classes'] = ''
        form = GroupForm(data=self.form_data)

        self.assertTrue(not form.is_valid())

    def test_create_group_form_is_valid_without_giving_name(self):
        # Testa se o formulário é válido sem que o usuário escolha as turmas do grupo.
        # Espera-se que form.is_valid() retorne False.
        self.form_data['name'] = ''
        self.form_data['avaliable_classes'] = ["('590861439156', 'Curso de exploração de dados com Pandas - Python')"]
        form = GroupForm(data=self.form_data)

        self.assertTrue(not form.is_valid())
