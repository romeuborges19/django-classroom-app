from django import forms
from classroom.api.api import GCApi
from classroom.models import Group



class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        exclude = ['classes']

    def __init__(self, *args, **kwargs):
        super(GroupForm, self).__init__(*args, **kwargs)
        api = GCApi()
        CLASSES = [(course['id'], course['name']) for course in api.get_courses()]

        self.fields['avaliable_classes'] = forms.MultipleChoiceField(
            choices=CLASSES,
            widget=forms.CheckboxSelectMultiple,
            required=False,
        )

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.classes = self.cleaned_data.get('avaliable_classes')

        if commit:
            instance.save()

        return instance

