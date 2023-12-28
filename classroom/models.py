from django.db import models

# Create your models here.

class Group(models.Model):
    # Model que armazena grupos de turmas

    name = models.CharField("Group Name", max_length=150)
    classes = models.JSONField("Classes")
    students = models.JSONField("Students", default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Lists(models.Model):
    # Model que armazena listas de alunos necessárias para gerenciamento de grupos de alunos 

    approved_list = models.JSONField("List of approved students", default=None, null=True)
    enrolled_list = models.JSONField("List of enrolled students", default=None, null=True)
    missing_list = models.JSONField("List of missing students", default=None, null=True)
    unknown_list = models.JSONField("List of unknown students", default=None, null=True)
    group = models.OneToOneField(Group, on_delete=models.CASCADE, related_name="group", default=None)
