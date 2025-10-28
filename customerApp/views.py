from django.shortcuts import render
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.db import IntegrityError
import secrets
import string
import boto3
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.conf import settings
from .models import Customer
from .forms import CustomerForm

def create_customer(request):
    if not request.user.is_superuser: 
        return redirect('login')
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            pwd = generate_password()
            print("Generated password:", pwd)
            try:
                # Create User account
                user = User.objects.create_user(
                    username=form.cleaned_data['email'],
                    email=form.cleaned_data['email'],
                    password=pwd,
                    first_name=form.cleaned_data['first_name'],
                    last_name=form.cleaned_data['last_name'],
                    is_superuser=False,
                    is_staff=False
                )
                
                # Create Customer record linked to User
                customer = form.save(commit=False)
                customer.user = user
                customer.save()

                # Send email with credentials
                try:
                    ses = boto3.client('ses', region_name=getattr(settings, 'AWS_REGION', 'us-east-1'))
                    ses.send_email(
                        Source=settings.DEFAULT_FROM_EMAIL,
                        Destination={'ToAddresses': [customer.email]},
                        Message={
                            'Subject': {'Data': 'Your Stock Management System Account'},
                            'Body': {'Text': {'Data': f"""Hello {customer.first_name}, Your account has been created! Login: {customer.email} Password: {pwd} Login at: http://yourdomain.com/login/ Best regards, Stock Management Team"""}}
                        }
                    )
                    messages.success(request, "Customer created and credentials emailed!")
                except Exception as e:
                    messages.warning(request, f"Customer created but email failed: {e}")
                return redirect('admin_dashboard')
            except IntegrityError:
                messages.error(request, "A user with this email already exists.")
            except Exception as e:
                messages.error(request, f"Error creating customer: {e}")   
    else:
        form = CustomerForm()
    return render(request, 'create_customer.html', {'form': form})

def edit_customer(request, customer_id):
    if not request.user.is_superuser: 
        return redirect('login')
    customer = get_object_or_404(Customer, id=customer_id)
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, "Customer updated.")
            return redirect('admin_dashboard')
    else:
        form = CustomerForm(instance=customer)
    return render(request, 'edit_customer.html', {'form': form, 'customer': customer})


def delete_customer(request, customer_id):
    if not request.user.is_superuser: 
        return redirect('login')
    customer = get_object_or_404(Customer, id=customer_id)
    if request.method == 'POST':
        customer.delete()
        messages.success(request, "Customer deleted.")
        return redirect('admin_dashboard')
    return render(request, 'confirm_delete_customer.html', {'customer': customer})

def generate_password(length=10):
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))