from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Stock
from .forms import StockForm
from customerApp.models import Customer
from requestApp.forms import StockRequestForm

from .dynamodb_stock import StockDB
from customerApp.dynamodb import CustomerDB
from requestApp.dynamodb_stockrequest import StockRequestDB

def create_stock(request):
    if not request.user.is_superuser: 
        return redirect('login')

    if request.method == 'POST':
        form = StockForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.cleaned_data
            image_file = request.FILES.get('image')
            StockDB.create(
                name=data['name'],
                category=data['category'],
                quantity=data['quantity'],
                price=data['price'],
                image_file=image_file
            )
            messages.success(request, "Stock item created.")
            return redirect('admin_dashboard')
    else:
        form = StockForm()
    return render(request, 'create_stock.html', {'form': form})


def edit_stock(request, stock_id):
    if not request.user.is_superuser:
        return redirect('login')

    stock = StockDB.get(stock_id)
    if not stock:
        messages.error(request, "Stock not found.")
        return redirect('admin_dashboard')

    if request.method == 'POST':
        form = StockForm(request.POST, request.FILES, initial=stock)
        if form.is_valid():
            data = {
                'name': form.cleaned_data['name'],
                'category': form.cleaned_data['category'],
                'quantity': form.cleaned_data['quantity'],
                'price': float(form.cleaned_data['price'])
            }
            new_image = request.FILES.get('image')
            StockDB.update(stock_id, data, new_image=new_image)
            messages.success(request, "Stock updated.")
            return redirect('admin_dashboard')
    else:
        form = StockForm(initial=stock)
    return render(request, 'edit_stock.html', {'form': form, 'stock': stock})


def delete_stock(request, stock_id):
    if not request.user.is_superuser:
        return redirect('login')

    stock = StockDB.get(stock_id)
    if not stock:
        messages.error(request, "Stock not found.")
        return redirect('admin_dashboard')

    if request.method == 'POST':
        StockDB.delete(stock_id)
        messages.success(request, "Stock deleted.")
        return redirect('admin_dashboard')
    return render(request, 'confirm_delete_stock.html', {'stock': stock})


def request_stock(request):
    if request.user.is_superuser:
        messages.error(request, "Admins cannot request stock.")
        return redirect('admin_dashboard')
    
    customer = CustomerDB.get(request.user.email)
    if not customer:
        messages.error(request, "Customer profile not found.")
        return redirect('customer_dashboard')

    if request.method == 'POST':
        form = StockRequestForm(request.POST)
        if form.is_valid():
            stock_id = form.cleaned_data['stock'].stock_id
            quantity = form.cleaned_data['quantity']
            StockRequestDB.create(
                customer_email=request.user.email,
                stock_id=stock_id,
                quantity=quantity
            )
            messages.success(request, "Stock request submitted successfully!")
            return redirect('customer_dashboard')
    else:
        form = StockRequestForm()

    available_stocks = StockDB.all()
    return render(request, 'request_stock.html', {
        'form': form,
        'available_stocks': available_stocks
    })
