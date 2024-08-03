from django.urls import path
from .views import *

urlpatterns =[
    path('members/<str:student_id>/', VerifyMemberAPIView.as_view()),
    # path('homework/', HomeworkAPIView.as_view())
]