from django.urls import path
from . import views

urlpatterns = [
    path('members/', views.list_members, name='members'),
]