from django.urls import path
from accounts import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('google/', views.google_oauth_view, name='google_oauth'),
    path('verify-email/<str:token>/', views.verify_email_view, name='verify_email'),
    path('resend-verification/', views.resend_verification_view, name='resend_verification'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('reset-password/<str:token>/', views.reset_password_view, name='reset_password'),
    path('profile/complete/', views.complete_profile_view, name='complete_profile'),
    path('profile/', views.profile_view, name='profile'),
    
    # Role-Based Dashboards
    path('dashboard/student/', views.student_dashboard, name='dashboard_student'),
    path('dashboard/parent/', views.parent_dashboard, name='dashboard_parent'),
    path('dashboard/admin/', views.admin_dashboard, name='dashboard_admin'),
]
