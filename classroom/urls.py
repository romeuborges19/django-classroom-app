from django.urls import path
from . import views

app_name='classroom'

urlpatterns=[
        path('', views.classroom_view, name='classroom')
]
