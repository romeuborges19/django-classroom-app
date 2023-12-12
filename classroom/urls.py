from django.urls import path
from . import views

app_name='classroom'

urlpatterns=[
    path('', views.ClassroomView.as_view(), name='home'),
    path('groups/create', views.ClassroomGroupCreateView.as_view(), name='create_group'),
]
