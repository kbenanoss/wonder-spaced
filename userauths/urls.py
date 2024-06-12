from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)
from userauths import views as userauths_views


urlpatterns = [
    path('register/', userauths_views.RegisterView.as_view(), name="register"),
    path('login/', userauths_views.LoginAPIView.as_view(), name="login"),
    path('logout/', userauths_views.LogoutAPIView.as_view(), name="logout"),
    path('email-verify/', userauths_views.VerifyEmail.as_view(), name="email-verify"),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('request-reset-email/', userauths_views.RequestPasswordResetEmail.as_view(),
         name="request-reset-email"),
    path('password-reset/<uidb64>/<token>/',
         userauths_views.PasswordTokenCheckAPI.as_view(), name='password-reset-confirm'),
    path('password-reset-complete', userauths_views.SetNewPasswordAPIView.as_view(),
         name='password-reset-complete'),
    
]
