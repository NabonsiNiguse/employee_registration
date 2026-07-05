from django.urls import path 
from .views import EmployeeLoginView

urlspattern = [
    path('api/login/'),EmployeeLoginView.as_view(), name='employee-login'
]