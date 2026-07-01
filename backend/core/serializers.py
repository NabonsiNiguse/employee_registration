# Serializers for the core app
# This file acts as a data translation layer between Django models and JSON.

from rest_framework import serializers  # ✓ የተስተካከለ (rest_framework)
from django.contrib.auth.models import User
from .models import Employee, Task

# ------------------------------------------------------------------------------
# 1. UserMiniSerializer
# ------------------------------------------------------------------------------
class UserMiniSerializer(serializers.ModelSerializer):  # ✓ የተስተካከለ (ModelSerializer እና ያለ 's')
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

# ------------------------------------------------------------------------------
# 2. EmployeeSerializer
# ------------------------------------------------------------------------------
class EmployeeSerializer(serializers.ModelSerializer):
    # virtual field - የሰራተኛውን መረጃ ከ User ሞዴል ይጠቀማል
    created_by_details = UserMiniSerializer(source='created_by', read_only=True)
    
    class Meta:
        model = Employee
        fields = ['id', 'name', 'email', 'department', 'created_by', 'created_by_details']
        extra_kwargs = {
            'created_by': {'write_only': True, 'required': False},
        }   

# ------------------------------------------------------------------------------
# 3. TaskSerializer
# ------------------------------------------------------------------------------
class TaskSerializer(serializers.ModelSerializer):  # ✓ የተስተካከለ (ModelSerializer እና ያለ 's')
    # ✓ የተስተካከለ (EmployeeSerializer ያለ 's')
    assigned_to_details = EmployeeSerializer(source='assigned_to', read_only=True)
    created_by_details = UserMiniSerializer(source='created_by', read_only=True)
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'status', 'due_date',
            'created_by', 'created_by_details', 'assigned_to',
            'assigned_to_details', 'created_at', 'updated_at'
        ]
        # ✓ የተስተካከለ (ወደ Meta ውስጥ በትክክል ገብቷል)
        extra_kwargs = {
            'created_by': {'write_only': True, 'required': False},
            'assigned_to': {'write_only': True},
        }
        