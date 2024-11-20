from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static

from django.contrib.auth import views as auth_views
from rest_framework.routers import DefaultRouter
from .views import UserProfileViewSet, PregnancyCheckupViewSet, CheckupVisitViewSet

router = DefaultRouter()
router.register(r'user-profiles', UserProfileViewSet)
router.register(r'pregnancy-checkups', PregnancyCheckupViewSet)
router.register(r'checkup-visits', CheckupVisitViewSet)
urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('profile/<int:user_id>/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('change-password/', views.change_password, name='change_password'),


    path('', views.home, name='home'),
    path('base/', views.base, name='base'),
    path('english-date/', views.english_date,
         name='english_date'),
    path('nepali-date/', views.nepali_date,
         name='nepali_date'),
    path('add-patient/', views.add_pregnancy_checkup,
         name='add_pregnancy_checkup'),

    path('checkup-list/', views.checkup_list, name='checkup_list'),
    path('delete/<int:checkup_id>/', views.delete_checkup, name='delete_checkup'),
    path('checkup/<str:patient_id>/', views.checkup_detail,
         name='checkup_detail'),  # Add this line for details
    path('checkup/<int:checkup_id>/record-visit/',
         views.record_visit, name='record_visit'),
    path('checkup/<int:checkup_id>/', views.checkup_detail, name='checkup_detail'),
    path('visit/edit/<int:visit_id>/', views.edit_visit, name='edit_visit'),
    #     path('pregnancy-calculator/', views.pregnancy_calculator,
    #          name='pregnancy_calculator'),






] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
