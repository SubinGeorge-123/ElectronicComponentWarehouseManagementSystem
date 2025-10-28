from django.urls import path
from .views import create_stock,edit_stock,delete_stock,request_stock

urlpatterns = [
    path('create_stock/', create_stock, name='create_stock'),
    path('edit_stock/<int:stock_id>/', edit_stock, name='edit_stock'),
    path('delete_stock/<int:stock_id>/', delete_stock, name='delete_stock'),
    path('request_stock/', request_stock, name='request_stock'),
]
