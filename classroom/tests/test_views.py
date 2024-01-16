from django.test import RequestFactory, TestCase
from django.urls import reverse

from classroom.models import Group, Lists
from classroom.views import ClassroomHomeView, GroupCreateView, GroupListView


class ClassroomViewsTest(TestCase):
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

        response = GroupCreateView.as_view()(request)
        self.assertEqual(response.status_code, 200)    

    def test_group_detail_view_is_correct(self):
        # Testa se a view de detalhe de grupo é carregada corretamente
        response = self.client.get(reverse(
            'classroom:group',
            kwargs={'pk': self.group.pk}
        ))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'test_group')

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
