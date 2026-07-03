from rest_framework import serializers 
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Employee, Task

# 1. UserMiniSerializer
class UserMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

# 2. EmployeeSerializer
class EmployeeSerializer(serializers.ModelSerializer):
    created_by_details = UserMiniSerializer(source='created_by', read_only=True)
    # የ 'related_name' ስህተትን ለማስተካከል 'assigned_tasks' ተጠቀመ
    task_assigned_to_details = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Employee
        fields = ['id', 'name', 'email', 'department', 'created_by', 'created_by_details', 'task_assigned_to_details']
        extra_kwargs = {'created_by': {'write_only': True, 'required': False}}

    def get_task_assigned_to_details(self, obj):
        from .serializers import TaskSerializer # Circular Import ለመፍታት
        tasks = obj.assigned_tasks.all() 
        return TaskSerializer(tasks, many=True).data

    def validate_email(self, value): # ትክክለኛው ስም
        if Employee.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already in use.")
        if not value.endswith('@gmail.com'):
            raise serializers.ValidationError("Email must be a Gmail address.")
        return value

# 3. TaskSerializer
class TaskSerializer(serializers.ModelSerializer):
    assigned_to_details = EmployeeSerializer(source='assigned_to', read_only=True)
    created_by_details = UserMiniSerializer(source='created_by', read_only=True)
    day_left = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'status', 'due_date',
            'created_by', 'created_by_details', 'assigned_to',
            'assigned_to_details', 'created_at', 'updated_at', 'day_left'
        ]
        extra_kwargs = {
            'created_by': {'write_only': True, 'required': False},
            'assigned_to': {'write_only': True},
        }

    # እነዚህ ሜተሮች ከ class Meta ውጪ መሆን አለባቸው!
    def get_day_left(self, obj):
        today = timezone.now().date()
        if obj.due_date > today:
            return (obj.due_date - today).days
        return 0 

    def validate(self, data):
        title = data.get('title', '')
        description = data.get('description', '')
        if title.lower() == description.lower():
            raise serializers.ValidationError("Title and description cannot be the same.")
        return data