from django.urls import path
from .views import create_customer,edit_customer,delete_customer

urlpatterns = [
    path('create_customer/', create_customer, name='create_customer'),
    path('edit_customer/<int:customer_id>/', edit_customer, name='edit_customer'),
    path('delete_customer/<int:customer_id>/', delete_customer, name='delete_customer'),
]
