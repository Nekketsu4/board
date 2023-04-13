from django.urls import path

from .views import *

app_name = 'main'
urlpatterns = [
    path('accounts/logout/', BoardLogoutView.as_view(), name='logout'),
    path('accounts/password/change/done/', BoardPasswordChangeDoneView.as_view(), name='password_change_done'),
    path('accounts/password/change/', BoardPasswordChangeView.as_view(), name='password_change'),
    path('accounts/profile/delete/', DeleteUserView.as_view(), name='profile_delete'),
    path('accounts/profile/change/', ChangeUserInfoView.as_view(), name='profile_change'),
    path('accounts/profile/change/<int:pk>/', profile_bboard_change, name='profile_bboard_change'),
    path('accounts/profile/delete/<int:pk>/', profile_bboard_delete, name='profile_bboard_delete'),
    path('accounts/profile/add/', profile_bboard_add, name='profile_bboard_add'),
    path('accounts/profile/<int:pk>/', profile_bboard_detail, name='profile_bboard_detail'),
    path('accounts/profile/', profile, name='profile'),
    path('accounts/register/activate/<str:sign>/', user_activate, name='register_activate'),
    path('accounts/register/done', RegisterDoneView.as_view(), name='register_done'),
    path('accounts/register/', RegisterUserView.as_view(), name='register'),
    path('accounts/login/', BoardLoginView.as_view(), name='login'),
    path('<int:rubric_pk>/<int:pk>/', detail, name='detail'),
    path('<int:pk>/', by_rubric, name='by_rubric'),
    path('<str:page>/', other_page, name='other'),
    path('', index, name='index'),
]
