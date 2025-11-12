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
from .dynamodb import CustomerDB

def create_customer(request):
    if not request.user.is_superuser:
        return redirect('login')

    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            pwd = generate_password()
            try:
                user = User.objects.create_user(
                    username=form.cleaned_data['email'],
                    email=form.cleaned_data['email'],
                    password=pwd,
                    first_name=form.cleaned_data['first_name'],
                    last_name=form.cleaned_data['last_name'],
                    is_superuser=False,
                    is_staff=False
                )

                # Save in DynamoDB
                CustomerDB.create(
                    user_id=user.id,
                    first_name=form.cleaned_data['first_name'],
                    last_name=form.cleaned_data['last_name'],
                    email=form.cleaned_data['email']
                )

                # Send credentials via SES
                ses = boto3.client('ses', region_name=getattr(settings, 'AWS_REGION', 'us-east-1'))
                ses.send_email(
                    Source=settings.DEFAULT_FROM_EMAIL,
                    Destination={'ToAddresses': [form.cleaned_data['email']]},
                    Message={
                        'Subject': {'Data': 'Your Stock Management Account'},
                        'Body': {'Text': {'Data': f"""Hello {form.cleaned_data['first_name']},
Your account has been created!

Login: {form.cleaned_data['email']}
Password: {pwd}
Login at: http://yourdomain.com/login/
"""}}}
                )
                messages.success(request, "Customer created and email sent!")
                return redirect('admin_dashboard')
            except Exception as e:
                messages.error(request, f"Error: {e}")
    else:
        form = CustomerForm()
    return render(request, 'create_customer.html', {'form': form})


def edit_customer(request, email):
    if not request.user.is_superuser:
        return redirect('login')

    customer = CustomerDB.get(email)
    if not customer:
        messages.error(request, "Customer not found.")
        return redirect('admin_dashboard')

    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            data = {
                'first_name': form.cleaned_data['first_name'],
                'last_name': form.cleaned_data['last_name']
            }
            CustomerDB.update(email, data)
            messages.success(request, "Customer updated.")
            return redirect('admin_dashboard')
    else:
        form = CustomerForm(initial=customer)
    return render(request, 'edit_customer.html', {'form': form, 'customer': customer})



def delete_customer(request, email):
    if not request.user.is_superuser:
        return redirect('login')

    if request.method == 'POST':
        CustomerDB.delete(email)
        messages.success(request, "Customer deleted.")
        return redirect('admin_dashboard')
    return render(request, 'confirm_delete_customer.html', {'email': email})


def generate_password(length=10):
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))