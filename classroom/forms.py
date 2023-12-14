from django import forms
from classroom.api.api import GCApi
from classroom.models import Group



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

