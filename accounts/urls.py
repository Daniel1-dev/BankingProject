from django.urls import path
from . import views

urlpatterns = [
    path('',views.landing,name='landing'),
    path("register/", views.register, name="register"),
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path('profile/',views.profile, name='profile'),

    # ... your other URLs ...
    path('transfer/', views.transfer, name='transfer'),  # ← ADD THIS LINE
    path('admin-dashboard/',views.admin_dashboard, name='admin_dashboard'),
    # accounts/urls.py
    path('admin-edit/<int:contribution_id>/', views.edit_contribution, name='admin_edit'),
    path('admin-profile/', views.admin_profile,name='admin_profile'),
    path('delete-contribution/<int:contribution_id>/',views.delete_contribution,name='delete_contribution'),
    path('suspend-user/<int:user_id>/',views.suspend_user,name='suspend_user'),
    path('admin-login/', views.admin_login_view,name='admin_login'),
    path('unsuspend-user/<int:user_id>/',views.unsuspend_user, name='unsuspend_user'),
    path('edit-user/<int:user_id>/',views.edit_user,name='edit_user'),
    path('verify-admin/', views.verify_admin, name='verify_admin'),
    path('update-weeks/',views.update_weeks,name='update_weeks'),
    path('change-weeks/', views.change_weeks,name='change_weeks'),
]