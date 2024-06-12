from django.urls import path, include
from site_settings import views as site_settings_views
from userauths import views as userauths_views
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

from rest_framework.routers import DefaultRouter
from main.views import CategoryViewSet, LessonViewSet, ActivityViewSet, PaymentViewSet, ProfileViewSet, UserViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'profiles', ProfileViewSet)

router.register(r'categories', CategoryViewSet)
router.register(r'lessons', LessonViewSet)
router.register(r'activities', ActivityViewSet)
router.register(r'payments', PaymentViewSet)




urlpatterns = [

    path('', include(router.urls)),
    
    path("site-settings/", site_settings_views.SiteSettingsListCreateAPIView.as_view(), name="sitesettings-list"),
    path("site-settings/<int:pk>/", site_settings_views.SiteSettingsDetailAPIView.as_view(), name="sitesettings-detail"),

]