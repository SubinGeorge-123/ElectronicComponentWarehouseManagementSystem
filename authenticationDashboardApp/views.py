from django.shortcuts import render, redirect
from django.contrib import messages
from authenticationDashboardApp.dynamodb_auth import UserDB  # Admin table
from customerApp.dynamodb import CustomerDB  # Customer table
import hashlib

# Password checker
def check_password(stored_hash, password):
    return stored_hash == hashlib.sha256(password.encode('utf-8')).hexdigest()

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # 1. Check in admin table first
        admin_user = UserDB.get_user(email)
        if admin_user and check_password(admin_user['password'], password):
            request.session['user_email'] = admin_user['email']
            request.session['is_superuser'] = admin_user.get('is_superuser', True)
            return redirect('admin_dashboard')

        # 2. If not found in admin table, check customer table
        customer_user = CustomerDB.get_user(email)
        if customer_user and check_password(customer_user['password'], password):
            request.session['user_email'] = customer_user['email']
            request.session['is_superuser'] = customer_user.get('is_superuser', False)
            return redirect('customer_dashboard')

        # 3. Invalid login
        messages.error(request, "Invalid email or password")

    return render(request, 'login.html')


def logout_view(request):
    request.session.flush()
    return redirect('login')


def admin_dashboard(request):
    if not request.session.get('is_superuser'):
        return redirect('login')
    users = UserDB.all_users()
    return render(request, 'admin_dashboard.html', {'users': users})


def customer_dashboard(request):
    if not request.session.get('user_email'):
        return redirect('login')
    # Fetch from either table if needed
    user = UserDB.get_user(request.session['user_email']) or CustomerDB.get_user(request.session['user_email'])
    return render(request, 'customer_dashboard.html', {'user': user})
