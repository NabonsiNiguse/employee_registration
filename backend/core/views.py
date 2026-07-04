from rest_framework import viewsets, permissions, filters 
from django.contrib.auth.models import User 
from .models import Employee, Task
from .serializers import EmployeeSerializer, TaskSerializer, UserMiniSerializer
 
  class EmployeeViewSet(viewSet.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission 