from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.db.models import Sum
from django.utils import timezone
from django.contrib.auth import update_session_auth_hash

from .models import Profile, Contribution, Payment
import uuid
from .forms import (
    ContributionForm,
    UserUpdateForm,
    ProfileUpdateForm,

)


from .models import (
    
    ContributionSettings
)




@login_required
def verify_admin(request):

    if request.method == "POST":

        password = request.POST.get(
            "password"
        )

        user = authenticate(
            request,
            username=request.user.username,
            password=password
        )

        if user and user.is_staff:

            request.session[
                "admin_verified"
            ] = True

            return redirect(
                "admin_dashboard"
            )

        messages.error(
            request,
            "Incorrect admin password"
        )

    return render(
        request,
        "verify_admin.html"
    )




# ======================
# TRANSFER VIEW
# ======================

@login_required
def transfer(request):

    profile = request.user.profile

    amount = profile.weekly_amount or 0

    if request.method == "POST":

        if amount <= 0:

            messages.error(
                request,
                "Weekly contribution amount not set."
            )

            return redirect(
                "dashboard"
            )

        Payment.objects.create(
            user=request.user,
            amount=amount
        )

        messages.success(
            request,
            "Transfer created successfully."
        )

        return redirect(
            "dashboard"
        )

    return render(
        request,
        "transfer.html",
        {
            "amount": amount,
            "account_number": "9048546775",
            "account_name": "Daniel Udeme Eyo",
            "bank_name": "Opay"
        }
    )


# ======================
# LOGIN VIEW
# ======================

# ======================
# LANDING PAGE
# ======================
def landing(request):
    return render(request, 'landing.html')



# ======================
# USER LOGIN
# ======================
def user_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if not user.is_active:
                messages.error(request, "Your account has been suspended.")
            else:
                login(request, user)
                return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password")

    return render(request, 'login.html')


# ======================
# LOGOUT
# ======================
@login_required
def user_logout(request):
    logout(request)
    return redirect('login')

def logout_view(request):

    request.session.pop(
        "admin_verified",
        None
    )

    logout(
        request
    )

    return redirect(
        "login"
    )
    
    
    
def login_view(request):
    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            if user.is_staff:
                return redirect(
                    "admin_dashboard"
                )

            return redirect(
                "dashboard"
            )

        messages.error(
            request,
            "Invalid username or password"
        )

    return render(
        request,
        "login.html"
    )
    
# ======================
# PROFILE
# ======================
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

    return render(
        request,
        'profile.html',
        {
            'user_form': user_form,
            'profile_form': profile_form
        }
    )


# ======================
# DASHBOARD
# ======================

# ======================
# CUSTOM ADMIN DASHBOARD
# ======================

# ======================
# EDIT CONTRIBUTION
# ======================
@staff_member_required
def edit_contribution(request, contribution_id):
    contribution = get_object_or_404(Contribution, id=contribution_id)

    if request.method == "POST":
        contribution.amount = request.POST.get("amount")
        contribution.status = request.POST.get("status")
        contribution.save()
        return redirect('admin_dashboard')

    return render(
        request,
        'edit_contribution.html',
        {
            'contribution': contribution
        }
    )

@staff_member_required
def admin_dashboard(request):

    if not request.user.is_staff:

        return redirect(
            "dashboard"
        )

    if not request.session.get(
        "admin_verified"
    ):

        return redirect(
            "verify_admin"
        )

    users = User.objects.all()

    contributions = Contribution.objects.all().order_by(
        "-contribution_date"
    )

    total_users = users.count()

    total_contributions = contributions.count()

    total_amount = contributions.filter(
        status="Paid"
    ).aggregate(
        Sum("amount")
    )["amount__sum"] or 0

    missed_count = contributions.filter(
        status="Missed"
    ).count()


    grouped_admin = {}


    for item in contributions:

        date = item.contribution_date.strftime(
            "%A %d %B %Y"
        )

        if date not in grouped_admin:

            grouped_admin[date] = {

                "items": [],
                "total": 0

            }

        grouped_admin[date]["items"].append(
            item
        )

        grouped_admin[date]["total"] += item.amount


    return render(
        request,
        "admin_dashboard.html",
        {
            "users": users,
            "contributions": contributions,
            "grouped_admin": grouped_admin,
            "total_users": total_users,
            "total_contributions": total_contributions,
            "total_amount": total_amount,
            "missed_count": missed_count
        }
    )
    
# ======================
# DELETE CONTRIBUTION
# ======================
@staff_member_required
def delete_contribution(request, contribution_id):
    contribution = get_object_or_404(Contribution, id=contribution_id)
    contribution.delete()
    return redirect('admin_dashboard')




@staff_member_required
def update_weeks(request):

    settings = ContributionSettings.objects.first()

    if not settings:

        settings = ContributionSettings.objects.create(
            total_weeks=12
        )

    if request.method=="POST":

        weeks=request.POST.get(
            "weeks"
        )

        settings.total_weeks=weeks
        settings.save()

        messages.success(
            request,
            "Contribution weeks updated successfully"
        )

        return redirect(
            "admin_dashboard"
        )

    return render(
        request,
        "update_weeks.html",
        {
            "settings":settings
        }
    )


# ======================
# EDIT USER
# ======================
@staff_member_required
def edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    profile = get_object_or_404(Profile, user=user)
    error = None

    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        weekly_amount = request.POST.get("weekly_amount")
        password = request.POST.get("password")

        # Only check duplicates if username changed
        if username != user.username:
            if User.objects.filter(username=username).exists():
                error = "Username already exists"
                return render(
                    request,
                    'edit_user.html',
                    {
                        'edit_user': user,
                        'profile': profile,
                        'error': error
                    }
                )

        user.username = username
        user.email = email
        profile.weekly_amount = weekly_amount

        if password:
            user.set_password(password)

        user.save()
        profile.save()

        return redirect('admin_dashboard')

    return render(
        request,
        'edit_user.html',
        {
            'edit_user': user,
            'profile': profile,
            'error': error
        }
    )


# ======================
# DASHBOARD
# ======================




# ======================
# ADMIN PROFILE
# ======================
@login_required
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

        # Prevent duplicate username
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

    return render(
        request,
        "admin_profile.html",
        {
            "success": success,
            "error": error,
            "profile": profile
        }
    )


def admin_login_view(request):

    if request.method == "POST":

        username = request.POST.get(
            "username"
        )

        password = request.POST.get(
            "password"
        )

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            if user.is_staff:

                login(
                    request,
                    user
                )

                return redirect(
                    'admin_dashboard'
                )

            else:

                messages.error(
                    request,
                    "This is not an admin account"
                )

        else:

            messages.error(
                request,
                "Invalid admin credentials"
            )

    return render(
        request,
        'admin_login.html'
    )

# ======================
# SUSPEND USER
# ======================
@staff_member_required
def suspend_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.is_active = False
    user.save()
    return redirect('admin_dashboard')


# ======================
# UNSUSPEND USER
# ======================
@staff_member_required
def unsuspend_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.is_active = True
    user.save()
    return redirect('admin_dashboard')
    




@login_required
def dashboard(request):

    profile = request.user.profile

    contributions = Contribution.objects.filter(
        user=request.user
    ).order_by(
        '-contribution_date'
    )

    weekly_amount = profile.weekly_amount or 0


    total = contributions.filter(
        status="Paid"
    ).aggregate(
        Sum("amount")
    )["amount__sum"] or 0


    if request.method == "POST":

        form = ContributionForm(
            request.POST
        )

        if form.is_valid():

            contribution = form.save(
                commit=False
            )

            if contribution.amount != weekly_amount:

                messages.error(
                    request,
                    "Amount must match your fixed contribution amount"
                )

                return redirect(
                    "dashboard"
                )

            contribution.user = request.user

            contribution.contribution_date = (
                timezone.now().date()
            )

            contribution.week_number = (
                timezone.now().isocalendar()[1]
            )

            contribution.status = "Paid"

            contribution.save()

            return redirect(
                "dashboard"
            )

    else:

        form = ContributionForm()


    settings, created = (
        ContributionSettings.objects.get_or_create(
            id=1,
            defaults={
                "total_weeks":12
            }
        )
    )

    total_weeks = settings.total_weeks


    target = (
        weekly_amount *
        total_weeks
    )


    progress = 0

    if target > 0:

        progress = round(
            (total / target) * 100,
            1
        )


    chart_labels = []
    chart_data = []


    for item in contributions:

        chart_labels.append(
            f"Week {item.week_number}"
        )

        chart_data.append(
            float(item.amount)
        )


    missed_count = contributions.filter(
        status="Missed"
    ).count()


    notifications=[]

    if missed_count > 0:

        notifications.append(
            f"You missed {missed_count} contribution(s)"
        )


    # GROUP CONTRIBUTIONS BY DATE
    grouped_contributions={}


    for contribution in contributions:

        contribution_date = (
            contribution.contribution_date
        )

        today = timezone.now().date()

        if contribution_date == today:

            date_label = (
                f"Today ({contribution_date})"
            )

        elif contribution_date == (
            today - timezone.timedelta(days=1)
        ):

            date_label = (
                f"Yesterday ({contribution_date})"
            )

        else:

            date_label = str(
                contribution_date
            )


        if date_label not in grouped_contributions:

            grouped_contributions[
                date_label
            ] = {

                "items":[],
                "total":0

            }


        grouped_contributions[
            date_label
        ]["items"].append(
            contribution
        )


        grouped_contributions[
            date_label
        ]["total"] += (
            contribution.amount
        )


    context={

        "form":form,
        "contributions":contributions,
        "grouped_contributions":grouped_contributions,
        "total":total,
        "target":target,
        "progress":progress,
        "weekly_amount":weekly_amount,
        "total_weeks":total_weeks,
        "chart_labels":chart_labels,
        "chart_data":chart_data,
        "notifications":notifications

    }

    return render(
        request,
        "dashboard.html",
        context
    )





# ======================
# CHANGE CONTRIBUTION WEEKS
# ======================

@login_required
@staff_member_required
def change_weeks(request):

    settings, created = (
        ContributionSettings.objects.get_or_create(
            id=1
        )
    )

    if request.method == "POST":

        weeks = request.POST.get(
            "total_weeks"
        )

        settings.total_weeks = weeks
        settings.save()

        messages.success(
            request,
            "Contribution weeks updated successfully"
        )

        return redirect(
            "admin_dashboard"
        )

    return render(
        request,
        "change_weeks.html",
        {
            "settings": settings
        }
    )
    
    
    
def register(request):

    if request.method == "POST":

        username = request.POST.get("username")
        full_name = request.POST.get("full_name")
        email = request.POST.get("email")
        weekly_amount = request.POST.get("weekly_amount")
        password = request.POST.get("password")

        # Check username exists
        if User.objects.filter(username=username).exists():

            messages.error(
                request,
                "Username already exists"
            )

            return redirect("register")

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        # Profile already created by signal.py
        profile = user.profile
        profile.full_name = full_name
        profile.weekly_amount = weekly_amount
        profile.save()

        messages.success(
            request,
            "Registration successful"
        )

        return redirect("login")

    return render(
        request,
        "register.html"
    )