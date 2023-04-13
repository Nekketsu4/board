from django.urls import path

from .views import bboards, BboardDetailView, comments

urlpatterns = [
    path('bboards/<int:pk>/comments/', comments),
    path('bboards/<int:pk>/', BboardDetailView.as_view()),
    path('bboards/', bboards),
]
