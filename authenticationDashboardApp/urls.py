from django.urls import path
from .views import login_view,admin_dashboard,logout_view,customer_dashboard

urlpatterns = [
    path('', login_view, name='login'),
    path('login/', login_view, name='login'),
    path('admin_dashboard/', admin_dashboard, name='admin_dashboard'),
    path('customer_dashboard/', customer_dashboard, name='customer_dashboard'),
    path('logout/', logout_view, name='logout'),
]
