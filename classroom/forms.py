from django import forms
from django.utils.translation import gettext as _

from classroom.api.api import GoogleAPI
from classroom.models import Group, Lists, Message
from classroom.utils import read_csv

RECIPIENTS = [
    ("matriculados", "Matriculados"),
    ("faltantes", "Faltantes"),
    ("aprovados", "Aprovados")
]

class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        exclude = ['classes', 'students', 'associated_form_id']

    def __init__(self, *args, **kwargs):
        super(GroupForm, self).__init__(*args, **kwargs)
        api = GoogleAPI()

        form_list = [('0', 'Nenhum')]
        form_list.extend([((form['id'], form['name'])) for form in api.get_forms()])

        CLASSES = [((course['id'], course['name']), course['name']) for course in api.get_courses()]
        FORMS = form_list

        self.fields['avaliable_classes'] = forms.MultipleChoiceField(
            choices=CLASSES,
            widget=forms.CheckboxSelectMultiple(),
            required=False,
            label="Turmas disponíveis"
        )

        self.fields['associated_form'] = forms.ChoiceField(
            choices=FORMS,
            widget=forms.Select(),
            required=False,
            label="Formulário associado",
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

        # O processo abaixo armazena os dados dos estudantes no atributo 'students',
        # ao criar o grupo de turmas
        instance.classes = self.cleaned_data.get('avaliable_classes')
        instance.classes = list(map(eval, instance.classes))

        api = GoogleAPI()
        classes_info = api.get_course_data([value[0] for value in instance.classes])
        students = []

        for i, course in enumerate(classes_info):
            students.append([instance.classes[i][1], course['students']])

        instance.students = students

        associated_form_id = self.cleaned_data.get('associated_form')
        if associated_form_id != 0:
            instance.associated_form_id = associated_form_id

        if commit:
            instance.save()

        return instance

class UpdateGroupForm(forms.ModelForm):
    # Formulário responsável por atualizar infomações do grupo
    class Meta:
        model = Group
        fields = ['name']

    def __init__(self, *args, **kwargs):
        super(UpdateGroupForm, self).__init__(*args, **kwargs)
        api = GoogleAPI()

        CLASSES = [((course['id'], course['name']), course['name']) for course in api.get_courses()]

        self.fields['avaliable_classes'] = forms.MultipleChoiceField(
            choices=CLASSES,
            widget=forms.CheckboxSelectMultiple,
            required=False,
            label="Turmas disponíveis",
        )

        self.initial = {
            'name': self.instance.name,
            'avaliable_classes': self._get_initial()
        }
        
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

        if commit:
            instance.save()

        return instance


    def _get_initial(self):
        initial = [f"('{course[0]}', '{course[1]}')" for course in self.instance.classes]

        return initial 

class ApprovedListCSVForm(forms.ModelForm):
    class Meta:
        model = Lists
        exclude = ['approved_list', 'missing_list', 'enrolled_list', 'unknown_list', 'group']

    def __init__(self, *args, **kwargs):
        super(ApprovedListCSVForm, self).__init__(*args, **kwargs)

        self.fields['approved_list_csv'] = forms.FileField()

    def clean(self):
        cleaned_data = super().clean()
        approved_list_csv = self.cleaned_data['approved_list_csv']

        if approved_list_csv:
            file_types = approved_list_csv.content_type.split('/')

            # Verifica se o arquivo é .csv
            if 'csv' not in file_types:
                # Caso não seja, envia mensagem de erro para o formulário
                raise forms.ValidationError(
                    _('Formato de arquivo inválido. Por favor, envie um arquivo .csv.'), 
                    code='invalid')
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

class ApprovedListGoogleFormsForm(forms.ModelForm):
    class Meta:
        model = Group
        exclude = ['name', 'classes', 'students', 'associated_form_id']

    def __init__(self, *args, **kwargs):
        super(ApprovedListGoogleFormsForm, self).__init__(*args, **kwargs)

        api = GoogleAPI()
        form_list = [('0', 'Nenhum')]
        form_list.extend([((form['id'], form['name'])) for form in api.get_forms()])
        FORMS = form_list

        self.fields['associated_form'] = forms.ChoiceField(
            choices=FORMS,
            widget=forms.Select(),
            required=False,
            label="Formulário associado",
        )

    def save(self, commit=True):
        instance = super().save(commit=False)

        associated_form_id = self.cleaned_data.get('associated_form')
        if associated_form_id != 0:
            instance.associated_form_id = associated_form_id

        if commit:
            instance.save()

        return instance

class EmailMessageForm(forms.Form):
    recipient = forms.ChoiceField(
        label="Destinatários",
        choices=RECIPIENTS,
        widget=forms.Select())
    subject = forms.CharField(label="Assunto", max_length=100)
    content = forms.CharField(label="Mensagem", widget=forms.Textarea())

    def clean(self):
        cleaned_data = super().clean()  
        
        if not cleaned_data.get('subject'):
            self.add_error('subject', forms.ValidationError(
                _('Você deve inserir um assunto no e-mail'),
                code='empty'))

        if not cleaned_data.get('content'):
            self.add_error('content', forms.ValidationError(
                _('O corpo do e-mail não pode estar vazio'),
                code='empty'))

        return cleaned_data


