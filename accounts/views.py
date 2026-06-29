from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Sum
from django.utils import timezone
from django.contrib.auth import update_session_auth_hash
import decimal
import requests
from django.conf import settings
from django.http import JsonResponse
import uuid

from .models import Profile, Transaction, Transfer
from .forms import UserUpdateForm, ProfileUpdateForm

@login_required
def dashboard(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    transactions = Transaction.objects.filter(user=request.user).order_by("-timestamp")
    
    total_deposits = transactions.filter(transaction_type="Deposit").aggregate(Sum("amount"))["amount__sum"] or 0
    total_withdrawals = transactions.filter(transaction_type="Withdrawal").aggregate(Sum("amount"))["amount__sum"] or 0
    total_transfers = transactions.filter(transaction_type="Transfer").aggregate(Sum("amount"))["amount__sum"] or 0

    context = {
        "transactions": transactions,
        "total_deposits": total_deposits,
        "total_withdrawals": total_withdrawals,
        "total_transfers": total_transfers,
    }
    return render(request, "dashboard.html", context)

@login_required
def transfer_money(request):
    if request.method == "POST":
        bank_code = request.POST.get("bank_code")
        account_number = request.POST.get("account_number")
        amount = float(request.POST.get("amount", 0))

        if amount > float(request.user.profile.balance):
            messages.error(request, "Insufficient balance.")
            return redirect("dashboard")

        headers = {"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}
        recipient_data = {
            "type": "nuban",
            "name": "Recipient",
            "account_number": account_number,
            "bank_code": bank_code,
            "currency": "NGN"
        }
        res = requests.post("https://api.paystack.co/transferrecipient", json=recipient_data, headers=headers)
        if res.status_code == 200:
            recipient_code = res.json()['data']['recipient_code']
            transfer_data = {"source": "balance", "reason": "Transfer", "amount": int(amount * 100), "recipient": recipient_code}
            transfer_res = requests.post("https://api.paystack.co/transfer", json=transfer_data, headers=headers)
            
            if transfer_res.status_code == 200:
                request.user.profile.balance -= decimal.Decimal(amount)
                request.user.profile.save()
                Transaction.objects.create(user=request.user, amount=amount, transaction_type="Transfer", description=f"Transfer to {account_number}")
                messages.success(request, "Transfer successful!")
            else:
                messages.error(request, "Transfer failed.")
        else:
            messages.error(request, "Could not verify recipient.")
            
        return redirect("dashboard")
    return render(request, "transfer_money.html")

def landing(request):
    return render(request, 'landing.html')

def user_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if hasattr(user, 'profile') and user.profile.is_suspended:
                return render(request, 'suspended.html', {'user': user})
            if not user.is_active:
                messages.error(request, "Your account is inactive.")
            else:
                login(request, user)
                return redirect('dashboard')
        else:
            # Check if this user exists and is suspended to provide specific feedback
            try:
                check_user = User.objects.get(username=username)
                if hasattr(check_user, 'profile') and check_user.profile.is_suspended:
                     return render(request, 'suspended.html', {'user': check_user})
            except User.DoesNotExist:
                pass
            
            messages.error(request, "Invalid username or password")
    return render(request, 'login.html')

@login_required
def user_logout(request):
    logout(request)
    return redirect('login')

@staff_member_required
def admin_profile(request):
    user = request.user
    profile = user.profile
    error = None
    success = None
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")
        profile_picture = request.FILES.get("profile_picture")
        existing = User.objects.filter(username=username).exclude(id=user.id)
        if existing.exists():
            error = "Username already exists"
        else:
            user.username = username
            user.email = email
            if profile_picture:
                profile.profile_picture = profile_picture
            if new_password:
                if new_password != confirm_password:
                    error = "Passwords do not match"
                else:
                    user.set_password(new_password)
            if not error:
                user.save()
                update_session_auth_hash(request, user)
                profile.save()
                success = "Profile updated successfully"
    return render(request, "admin_profile.html", {"success": success, "error": error, "profile": profile})

@login_required
def profile(request):
    if request.method == "POST":
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Profile updated successfully")
            return redirect('profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)
    return render(request, 'profile.html', {'user_form': user_form, 'profile_form': profile_form})

@staff_member_required
def admin_dashboard(request):
    if not request.user.is_staff:
        return redirect("dashboard")
    if not request.session.get("admin_verified"):
        return redirect("verify_admin")

    users = User.objects.all()
    transactions = Transaction.objects.all()

    total_users = users.count()
    total_deposits = transactions.filter(transaction_type="Deposit").aggregate(Sum("amount"))["amount__sum"] or 0
    total_withdrawals = transactions.filter(transaction_type="Withdrawal").aggregate(Sum("amount"))["amount__sum"] or 0
    total_transfers = transactions.filter(transaction_type="Transfer").aggregate(Sum("amount"))["amount__sum"] or 0
    total_balance = Profile.objects.aggregate(Sum("balance"))["balance__sum"] or 0

    return render(request, "admin_dashboard.html", {
        "users": users,
        "total_users": total_users,
        "total_deposits": total_deposits,
        "total_withdrawals": total_withdrawals,
        "total_transfers": total_transfers,
        "total_balance": total_balance,
    })

@staff_member_required
def admin_profile(request):
    user = request.user
    profile = user.profile
    error = None
    success = None
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")
        profile_picture = request.FILES.get("profile_picture")
        existing = User.objects.filter(username=username).exclude(id=user.id)
        if existing.exists():
            error = "Username already exists"
        else:
            user.username = username
            user.email = email
            if profile_picture:
                profile.profile_picture = profile_picture
            if new_password:
                if new_password != confirm_password:
                    error = "Passwords do not match"
                else:
                    user.set_password(new_password)
            if not error:
                user.save()
                update_session_auth_hash(request, user)
                profile.save()
                success = "Profile updated successfully"
    return render(request, "admin_profile.html", {"success": success, "error": error, "profile": profile})

@staff_member_required
def verify_admin(request):
    if request.method == "POST":
        password = request.POST.get("password")
        user = authenticate(request, username=request.user.username, password=password)
        if user and user.is_staff:
            request.session["admin_verified"] = True
            return redirect("admin_dashboard")
        messages.error(request, "Incorrect admin password")
    return render(request, "verify_admin.html")

def admin_login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_staff:
                login(request, user)
                return redirect('admin_dashboard')
            else:
                messages.error(request, "This is not an admin account")
        else:
            messages.error(request, "Invalid admin credentials")
    return render(request, 'admin_login.html')

@staff_member_required
def suspend_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    reason = request.POST.get("reason", "Policy violation")
    user.is_active = False
    user.profile.is_suspended = True
    user.profile.suspension_reason = reason
    user.profile.suspended_at = timezone.now()
    user.save()
    user.profile.save()
    return redirect('admin_dashboard')

@staff_member_required
def unsuspend_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.is_active = True
    user.profile.is_suspended = False
    user.profile.suspension_reason = ""
    user.profile.suspended_at = None
    user.save()
    user.profile.save()
    return redirect('admin_dashboard')

@staff_member_required
def edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    profile = get_object_or_404(Profile, user=user)
    error = None
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        if username != user.username and User.objects.filter(username=username).exists():
            error = "Username already exists"
        else:
            user.username = username
            user.email = email
            if password:
                user.set_password(password)
            user.save()
            profile.save()
            return redirect('admin_dashboard')
    return render(request, 'edit_user.html', {'edit_user': user, 'profile': profile, 'error': error})

def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        full_name = request.POST.get("full_name")
        gender = request.POST.get("gender")
        email = request.POST.get("email")
        phone_number = request.POST.get("phone_number")
        address = request.POST.get("address")
        profile_picture = request.FILES.get("profile_picture")
        password = request.POST.get("password")
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect("register")
        user = User.objects.create_user(username=username, email=email, password=password)
        profile = user.profile
        profile.full_name = full_name
        profile.gender = gender
        profile.phone_number = phone_number
        profile.address = address
        if profile_picture:
            profile.profile_picture = profile_picture
        profile.save()
        messages.success(request, "Registration successful")
        return redirect("login")
    return render(request, "register.html")

@login_required
def deposit(request):
    if request.method == "POST":
        amount = float(request.POST.get("amount", 0))
        if amount > 0:
            request.user.profile.balance += decimal.Decimal(amount)
            request.user.profile.save()
            Transaction.objects.create(user=request.user, amount=amount, transaction_type="Deposit", description="Wallet Deposit")
            messages.success(request, f"Successfully deposited ₦{amount:.2f}")
        return redirect("dashboard")
    return render(request, "deposit.html", {"account_number": "9048546775", "account_name": "Daniel Udeme Eyo", "bank_name": "Opay"})

@login_required
def withdraw(request):
    if request.method == "POST":
        amount = float(request.POST.get("amount", 0))
        if amount > 0 and request.user.profile.balance >= amount:
            request.user.profile.balance -= decimal.Decimal(amount)
            request.user.profile.save()
            Transaction.objects.create(user=request.user, amount=amount, transaction_type="Withdrawal", description="Wallet Withdrawal")
            messages.success(request, f"Successfully withdrew ₦{amount:.2f}")
        else:
            messages.error(request, "Insufficient balance.")
        return redirect("dashboard")
    return render(request, "withdraw.html")

@login_required
def transactions_history(request):
    transactions = Transaction.objects.filter(user=request.user).order_by("-timestamp")
    return render(request, "transactions_history.html", {"transactions": transactions})

@login_required
def services(request):
    return render(request, 'services.html')

@login_required
def airtime(request):
    if request.method == "POST":
        messages.success(request, "Airtime purchase successful!")
        return redirect('services')
    return render(request, 'airtime.html')

@login_required
def data(request):
    if request.method == "POST":
        messages.success(request, "Data purchase successful!")
        return redirect('services')
    return render(request, 'data.html')

@login_required
def bills(request):
    if request.method == "POST":
        messages.success(request, "Bill payment successful!")
        return redirect('services')
    return render(request, 'bills.html')

@login_required
def resolve_account(request):
    account_number = request.GET.get('account_number')
    bank_code = request.GET.get('bank_code')
    headers = {"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}
    url = f"https://api.paystack.co/bank/resolve?account_number={account_number}&bank_code={bank_code}"
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        return JsonResponse(res.json()['data'])
    return JsonResponse({"error": "Account not found"}, status=400)
