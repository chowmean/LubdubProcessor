from django.urls import path

from . import views

urlpatterns = [
    path('index', views.index, name='index'),
    path('', views.submit, name='submit'),
    path('cpu_info', views.get_cpu_info, name='get_cpu_info')
]
