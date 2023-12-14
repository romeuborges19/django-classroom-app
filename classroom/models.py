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
