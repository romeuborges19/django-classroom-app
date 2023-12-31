from django.urls import path
from . import views

app_name='classroom'

urlpatterns=[
    path('', views.ClassroomHomeView.as_view(), name='home'),
    path('groups/', views.GroupListView.as_view(), name='groups'),
    path('groups/<int:pk>', views.GroupDetailView.as_view(), name='group'),
    path('groups/missing/<int:pk>', views.MissingStudentsView.as_view(), name='missing'),
    path('groups/create', views.GroupCreateView.as_view(), name='create_group'),
]
