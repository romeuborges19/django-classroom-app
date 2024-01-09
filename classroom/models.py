from django.db import models

# Create your models here.

class GroupManager(models.Manager):
    def find(self, id):
        return self.filter(id=id).first()

class Group(models.Model):
    # Model que armazena grupos de turmas

    name = models.CharField("Group Name", max_length=150)
    classes = models.JSONField("Classes")
    students = models.JSONField("Students", default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    objects = GroupManager()

    def __str__(self):
        return self.name

class ListsManager(models.Manager):
    def find_by_group_id(self, group_id):
        return self.filter(group_id=group_id).first()

class Lists(models.Model):
    # Model que armazena listas de alunos necessárias para gerenciamento de grupos de alunos 

    approved_list = models.JSONField("List of approved students", default=None, null=True)
    enrolled_list = models.JSONField("List of enrolled students", default=None, null=True)
    missing_list = models.JSONField("List of missing students", default=None, null=True)
    unknown_list = models.JSONField("List of unknown students", default=None, null=True)
    group = models.OneToOneField(Group, on_delete=models.CASCADE, related_name="group", default=None)

    objects = ListsManager()
