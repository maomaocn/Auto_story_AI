# apps/test/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Retrieve task list
     path('', views.task_list, name='task_list'), # tasks/ 会映射到这里
    path('create/', views.create, name='detail'),  # tasks/detail/
]