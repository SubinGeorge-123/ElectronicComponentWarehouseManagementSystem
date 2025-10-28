from django.shortcuts import render
from django.views.decorators.cache import never_cache
from .forms import LoginForm
from django.contrib.auth import login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from customerApp.models import Customer
from stockApp.models import Stock
from requestApp.models import StockRequest

@never_cache
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if user.is_superuser:
                return redirect('admin_dashboard')
            else:
                return redirect('customer_dashboard')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

# Admin Dashboard
def admin_dashboard(request):
    if not request.user.is_superuser:
        messages.error(request, "Only admin can access this page.")
        return redirect('login')

    stocks = Stock.objects.all()
    customers = Customer.objects.all()
    pending_requests = StockRequest.objects.filter(status='PENDING').order_by('-created_at')
    context = {'stocks': stocks, 'customers': customers, 'pending_requests': pending_requests}
    return render(request, 'admin_dashboard.html', context)

@never_cache
@login_required(login_url='login')
def customer_dashboard(request):
    if request.user.is_superuser:
        messages.error(request, "Admins cannot access customer dashboard.")
        return redirect('admin_dashboard')
    
    try:
        customer = Customer.objects.get(email=request.user.email)
        approved_requests = StockRequest.objects.filter(
            customer=customer, 
            status='APPROVED'
        ).order_by('-created_at')
        user_requests = StockRequest.objects.filter(
            customer=customer
        ).order_by('-created_at')
        available_stocks = Stock.objects.filter(quantity__gt=0)
        context = {
            'approved_requests': approved_requests,
            'user_requests': user_requests,
            'available_stocks': available_stocks,
        }
        return render(request, 'customer_dashboard.html', context)
        
    except Customer.DoesNotExist:
        messages.error(request, "Customer profile not found.")
        return redirect('login')
    
@never_cache
@login_required(login_url='login')
def logout_view(request):
    logout(request)
    return redirect('login')