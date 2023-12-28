from django.contrib import admin

from classroom.models import ApprovedList, Group
# Register your models here.

admin.site.register(Group)
admin.site.register(ApprovedList)
