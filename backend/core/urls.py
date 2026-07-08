from django.urls import path 
from .views import EmployeeLoginView, AdvancedLoginView

urlspattern = [
    path('api/login/'),AdvancedLoginView.as_view(), name='employee-login'     
]
