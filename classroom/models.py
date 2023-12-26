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

class ApprovedList(models.Model):
    # Model que armazena lista de alunos aprovados para um grupo de turmas

    approved_list = models.JSONField("List of approved students", default=None)
    not_missing_list = models.JSONField("List of not missing students", default=None) # Estudantes com e-mail diferente do registrado na lista de aprovados
    missing_list = models.JSONField("List of missing students", default=None) # Estudantes que realmente não estão matriculados na turma
    group = models.OneToOneField(Group, on_delete=models.CASCADE, related_name="group", default=None)
