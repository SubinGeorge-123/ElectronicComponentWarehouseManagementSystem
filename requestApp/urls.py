from django.urls import path
from .views import  proceed_request

urlpatterns = [
    path('proceed_request/<int:req_id>/', proceed_request, name='proceed_request'),
]
