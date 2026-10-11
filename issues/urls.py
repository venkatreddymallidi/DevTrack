from django.urls import path

from .views import issues_view, reporters_view

urlpatterns = [
    path('reporters/', reporters_view, name='reporters'),
    path('issues/', issues_view, name='issues'),
]
