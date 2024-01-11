from django import forms

from classroom.api.api import ClassroomAPI
from classroom.models import Group, Lists
from classroom.services import InvalidFileFormatError
from classroom.utils import read_csv
from django.utils.translation import gettext as _

class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        exclude = ['classes', 'students']

    def __init__(self, *args, **kwargs):
        super(GroupForm, self).__init__(*args, **kwargs)
        api = ClassroomAPI()

        CLASSES = [((course['id'], course['name']), course['name']) for course in api.get_courses()]

        self.fields['avaliable_classes'] = forms.MultipleChoiceField(
            choices=CLASSES,
            widget=forms.CheckboxSelectMultiple,
            required=False,
            label="Turmas disponíveis"
        )

    def clean(self):
        cleaned_data = super().clean()

        if not cleaned_data.get('name'):
            self.add_error('name', forms.ValidationError(
                _('O nome do grupo não pode ser vazio.'), 
                code='empty')) 
        
        if not cleaned_data.get('avaliable_classes'):
            self.add_error('avaliable_classes', forms.ValidationError(
                _('Selecione pelo menos uma turma para fazer parte do grupo.'),
                code='empty')) 

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.classes = self.cleaned_data.get('avaliable_classes')
        instance.classes = list(map(eval, instance.classes))

        api = ClassroomAPI()
        classes_info = api.get_course_data([value[0] for value in instance.classes])
        students = []

        for i, course in enumerate(classes_info):
            students.append([instance.classes[i][1], course['students']])

        instance.students = students

        if commit:
            instance.save()

        return instance

class ApprovedListForm(forms.ModelForm):
    class Meta:
        model = Lists
        exclude = ['approved_list', 'missing_list', 'enrolled_list', 'unknown_list', 'group']

    def __init__(self, *args, **kwargs):
        super(ApprovedListForm, self).__init__(*args, **kwargs)

        self.fields['approved_list_csv'] = forms.FileField()

    def clean(self):
        cleaned_data = super().clean()
        approved_list_csv = self.cleaned_data['approved_list_csv']

        if approved_list_csv:
            file_types = approved_list_csv.content_type.split('/')

            # Verifica se o arquivo é .csv
            if 'csv' not in file_types:
                # Caso não seja, envia mensagem de erro para o formulário
                self.add_error('approved_list_csv', forms.ValidationError(
                    _('Formato de arquivo inválido. Por favor, envie um arquivo .csv.'), 
                    code='invalid'))
            else: 
                # Caso seja, lê e armazena os dados do arquivo
                approved_list_data = read_csv(approved_list_csv.file)

                self.cleaned_data['approved_list'] = approved_list_data

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.approved_list = self.cleaned_data['approved_list']

        if commit:
            instance.save()

        return instance


