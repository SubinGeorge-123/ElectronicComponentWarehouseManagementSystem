from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Stock
from .forms import StockForm
from customerApp.models import Customer
from requestApp.forms import StockRequestForm

def create_stock(request):
    if not request.user.is_superuser: 
        return redirect('login')
    if request.method == 'POST':
        form = StockForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Stock item created.")
            return redirect('admin_dashboard')
    else:
        form = StockForm()
    return render(request, 'create_stock.html', {'form': form})

def edit_stock(request, stock_id):
    if not request.user.is_superuser: 
        return redirect('login')

    stock = get_object_or_404(Stock, id=stock_id)
    if request.method == 'POST':
        form = StockForm(request.POST, request.FILES, instance=stock)
        if form.is_valid():
            form.save()
            messages.success(request, "Stock updated.")
            return redirect('admin_dashboard')
    else:
        form = StockForm(instance=stock)
    return render(request, 'edit_stock.html', {'form': form, 'stock': stock})

def delete_stock(request, stock_id):
    if not request.user.is_superuser: 
        return redirect('login')

    stock = get_object_or_404(Stock, id=stock_id)
    if request.method == 'POST':
        stock.delete()
        messages.success(request, "Stock deleted.")
        return redirect('admin_dashboard')
    return render(request, 'confirm_delete_stock.html', {'stock': stock})

def request_stock(request):
    if request.user.is_superuser:
        messages.error(request, "Admins cannot request stock.")
        return redirect('admin_dashboard')
    
    try:
        customer = Customer.objects.get(email=request.user.email)
    except Customer.DoesNotExist:
        messages.error(request, "Customer profile not found.")
        return redirect('customer_dashboard')

    if request.method == 'POST':
        form = StockRequestForm(request.POST)
        if form.is_valid():
            stock_req = form.save(commit=False)
            stock_req.customer = customer
            stock_req.status = 'PENDING'
            stock_req.save()

            messages.success(request, "Stock request submitted successfully!")
            return redirect('customer_dashboard')
    else:
        form = StockRequestForm()
    
    available_stocks = Stock.objects.filter(quantity__gt=0)
    return render(request, 'request_stock.html', {
        'form': form, 
        'available_stocks': available_stocks
    })
