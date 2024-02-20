from django.urls import path
from . import views

app_name='classroom'

urlpatterns=[
    path('', views.ClassroomHomeView.as_view(), name='home'),
    path('groups/', views.GroupListView.as_view(), name='groups'),
    path('groups/<int:pk>', views.GroupDetailView.as_view(), name='group'),
    path('groups/missing/<int:pk>', views.MissingStudentsView.as_view(), name='missing'),
    path('groups/create', views.GroupCreateView.as_view(), name='create_group'),
    path('groups/delete', views.ProcessDeleteGroupView.as_view(), name='delete_group'),
    path('groups/update/<int:pk>', views.GroupUpdateView.as_view(), name='update_group'),
    path('groups/process-list', views.ProcessSetApprovedStudentsListView.as_view(), name="set_approved_list"),
    path('groups/process-forms-list', views.ProcessSetApprovedStudentsListFromFormsView.as_view(), name="set_approved_list_google"),
    path('groups/<int:pk>/email-students', views.EmailStudentsView.as_view(), name="send_email"),
    path('groups/<int:pk>/email-students/send', views.SendInvitationsView.as_view(), name="invite"),
    path('groups/<int:pk>/messages', views.EmailMessagesView.as_view(), name="messages"),
    path('forms/<int:pk>', views.AssociateForm.as_view(), name="forms")

]
