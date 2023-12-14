from django import forms
from django.contrib.admin.options import widgets
from classroom.api.api import GCApi
from classroom.models import ApprovedList, Group



class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        exclude = ['classes', 'students']

    def __init__(self, *args, **kwargs):
        super(GroupForm, self).__init__(*args, **kwargs)
        api = GCApi()

        CLASSES = [((course['id'], course['name']), course['name']) for course in api.get_courses()]

        self.fields['avaliable_classes'] = forms.MultipleChoiceField(
            choices=CLASSES,
            widget=forms.CheckboxSelectMultiple,
            required=False,
        )

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.classes = self.cleaned_data.get('avaliable_classes')
        instance.classes = list(map(eval, instance.classes))

        api = GCApi()
        classes_info = api.get_course_data([value[0] for value in instance.classes])
        students = []

        i = 0
        for course in classes_info:
            students.append([instance.classes[i][1], course['students']])
            i += 1

        instance.students = students

        if commit:
            instance.save()

        return instance

class ApprovedListForm(forms.ModelForm):
    class Meta:
        model = ApprovedList
        exclude = ['approved_list', 'group']

    def __init__(self, *args, **kwargs):
        super(ApprovedListForm, self).__init__(*args, **kwargs)
        
        self.fields['approved_list_input'] = forms.CharField(
            widget=forms.TextInput(
                attrs={
                    'class':'form-control', 
                    'placeholder':'Insert list of approved students'
                }
            )
        )

    def clean(self):
        print('limpando')
        cleaned_data = super().clean()

        approved_list = self.cleaned_data.get('approved_list_input')
        approved_list = approved_list.split(' ')
        self.cleaned_data['approved_list'] = approved_list
        print(self.cleaned_data['approved_list'])
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)

        instance.approved_list = self.cleaned_data['approved_list']

        if commit:
            instance.save()

        return instance
