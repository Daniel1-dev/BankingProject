from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing, name='landing'),
    path("register/", views.register, name="register"),
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name='user_logout'),
    path("dashboard/", views.dashboard, name="dashboard"),
    path('settings/', views.settings, name='settings'),
    path('deposit/', views.deposit, name='deposit'),
    path('withdraw/', views.withdraw, name='withdraw'),
    path('transactions-history/', views.transactions_history, name='transactions_history'),
    path('resolve-account/', views.resolve_account, name='resolve_account'),
    path('transfer-money/', views.transfer_money, name='transfer_money'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-profile/', views.admin_profile, name='admin_profile'),
    path('suspend-user/<int:user_id>/', views.suspend_user, name='suspend_user'),
    path('unsuspend-user/<int:user_id>/', views.unsuspend_user, name='unsuspend_user'),
    path('edit-user/<int:user_id>/', views.edit_user, name='edit_user'),
    path('verify-admin/', views.verify_admin, name='verify_admin'),
    path('admin-login/', views.admin_login_view, name='admin_login'),
    path('services/', views.services, name='services'),
    path('airtime/', views.airtime, name='airtime'),
    path('data/', views.data, name='data'),
    path('bills/', views.bills, name='bills'),
    path('download-db/', views.download_db, name='download_db'),
]