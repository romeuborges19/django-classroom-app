import csv
from io import StringIO
from typing import List
from django.test import RequestFactory, TestCase
from django.urls import reverse
from requests.exceptions import MissingSchema
from classroom.models import Group, Lists

from classroom.views import ClassroomHomeView, GroupDetailView, GroupListView, MissingStudentsView

# Create your tests here.

class ClassroomURLsTest(TestCase):
    def test_home_url_is_correct(self):
        # Testa se a URL da home é carregada corretamente
        home_url = reverse('classroom:home')

        self.assertEqual(home_url, '/')

    def test_groups_url_is_correct(self):
        # Testa se a URL da página que carrega os grupos é carregada corretamente
        groups_url = reverse('classroom:groups')

        self.assertEqual(groups_url, '/groups/')

    def test_create_group_url_is_correct(self):
        # Testa se a URL da página de criação de grupos é carregada corretamente
        create_group_url = reverse('classroom:create_group')

        self.assertEqual(create_group_url, '/groups/create')

    def test_group_detail_url_is_correct(self):
        # Testa se a URL da página de detalhe dos grupos é carregada corretamente
        group_detail_url = reverse(
            'classroom:group', 
            kwargs={'pk': 5}
        )

        self.assertEqual(group_detail_url, '/groups/5')

    def test_missing_students_url_is_correct(self):
        # Testa se a URL da página de gerenciamento de alunos faltantes é carregada
        # corretamente
        missing_students_url = reverse(
            'classroom:missing',
            kwargs={'pk': 5}
        )

        self.assertEqual(missing_students_url, '/groups/missing/5')

class ClassroomViewsTest(TestCase):
    # Esta classe contém testes de views simples, que não exigem muitos dados para
    # seu funcionamento

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

    def test_home_view_is_correct(self):
        # Testa se a view de home está sendo carregada corretamente
        request = self.factory.get('/')

        response = ClassroomHomeView.as_view()(request)
        self.assertEqual(response.status_code, 200)

    def test_groups_view_is_correct(self):
        # Testa se a view de listagem de grupos é carregada corretamente
        request = self.factory.get(reverse('classroom:groups'))

        response = GroupListView.as_view()(request)
        self.assertEqual(response.status_code, 200)

    def test_create_group_view_is_correct(self):
        # Testa se a view de criação de grupo é carregada corretamente
        request = self.factory.get(reverse('classroom:create_group'))

        response = GroupListView.as_view()(request)
        self.assertEqual(response.status_code, 200)    
        
class GroupDetailViewTest(TestCase):
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
        self.csv_file_content =[['fullname', 'email'], 
                                ['Gabriel Reis Nadler Prata','gabrielreisnp@gmail.com'],
                                ['Rafael Mansilha Murta','rafael.mansilha@gmail.com'],
                                ['Eduardo de Sá Coêlho Ribeiro Costa','eduardodesacoelho08@gmail.com']]

    def test_group_detail_view_is_correct(self):
        # Testa se a view de detalhe de grupo é carregada corretamente
        response = self.client.get(reverse(
            'classroom:group',
            kwargs={'pk': self.group.pk}
        ))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'test_group')


    def test_approved_students_list_is_set_correctly(self):
        with open('test_file.csv', 'w', newline='') as csv_file:
            wr = csv.writer(csv_file, quoting=csv.QUOTE_ALL)
            wr.writerow(self.csv_file_content)

            response = self.client.post(reverse(
                'classroom:group',
                kwargs={'pk': self.group.pk}
            ), {'approved_list_csv': csv_file}) 

        self.assertEqual(response.status_code, 200)

class MissingStudentsViewTest(TestCase):
    # Esta classe reúne testes para a view de gerenciamento de alunos faltantes,
    # que exige maior número de dados para seu funcionamento.

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

    def test_missing_students_view_is_correct(self):
        # Testa se a view está sendo carregada corretamente
        response = self.client.get(reverse(
            'classroom:missing',
            kwargs={'pk': self.group.pk}
        ))

        self.assertEqual(response.status_code, 200)
