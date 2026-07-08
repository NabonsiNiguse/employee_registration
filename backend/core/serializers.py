from django.utils import timezone
from .models import Employee, Task
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import transaction

# ==============================================================================
# 0. AdvancedLoginSerializer: ለሎግ-ኢን ማጣሪያ እና ቶከን ማመንጫ
# ==============================================================================
from rest_framework import serializers
from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Employee, Task

# ==============================================================================
# SECTION 1: AUTHENTICATION & USER MANAGEMENT
# ==============================================================================

class AdvancedLoginSerializer(serializers.Serializer):
    """
    ተጠቃሚው በኢሜይል እና በፓስወርድ እንዲገባ የሚያስችል ሴሪያላይዘር።
    የሎግኢን መረጃን ብቻ ይቀበላል (Write-only) እና ቶከን ይመልሳል።
    """
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
     
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        # ተጠቃሚው መኖሩን እና ፓስወርዱ ትክክል መሆኑን እናረጋግጣለን
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError('Invalid email or password.')
        
        if not user.check_password(password):
            raise serializers.ValidationError('Invalid email or password.')
        
        if not user.is_active:
            raise serializers.ValidationError('User account is not active.')
            
        # ቶከን ማመንጨት
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'username': user.username,
            'email': user.email,
            'message': 'Login successful.'
        }

class UserMiniSerializer(serializers.ModelSerializer):
    """ዩዘርን እንደ Read-only መረጃ ለሌሎች ፊልዶች (ለምሳሌ 'Created by') ለማሳየት ይጠቅማል።"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

# ==============================================================================
# SECTION 2: EMPLOYEE MANAGEMENT
# ==============================================================================

class EmployeeSerializer(serializers.ModelSerializer):
    """
    ሰራተኛን ለመመዝገብ እና የስራ መረጃውን ለማሳየት።
    ከተጠቃሚው የሚመጣውን ኔትወርክ ዳታ ወደ User እና Employee ቴብል ይከፋፍላል።
    """
    password = serializers.CharField(write_only=True, required=True)
    created_by_details = UserMiniSerializer(source='created_by', read_only=True)
    # Circular import ለመፍታት ከፈንክሽኑ ውስጥ TaskSerializer ይጠራል
    task_assigned_to_details = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Employee
        fields = ['id', 'name', 'email', 'department', 'password', 'created_by', 'created_by_details', 'task_assigned_to_details']
        extra_kwargs = {'created_by': {'write_only': True, 'required': False}}

    def get_task_assigned_to_details(self, obj):
        from .serializers import TaskSerializer
        return TaskSerializer(obj.assigned_tasks.all(), many=True).data

    def validate_email(self, value): 
        """ኢሜይል መደጋገም እንደሌለበት እና በጂሜይል ማለቅ እንዳለበት ያረጋግጣል።"""
        if Employee.objects.filter(email=value).exists() or User.objects.filter(email=value).exists():
            raise serializers.ValidationError("ይህ ኢሜይል ቀድሞ ተመዝግቧል።")
        if not value.endswith('@gmail.com'):
            raise serializers.ValidationError("ኢሜይል የግድ '@gmail.com' መሆን አለበት።")
        return value
        
    def create(self, validated_data):
        """
        transaction.atomic የሚጠቀምበት ምክንያት፦ User ወይም Employee መፈጠር ካልተሳካ 
        ሁለቱም እንዳይፈጠሩ (Rollback) በማድረግ የዳታቤዝ ኢንተግሪቲን ለመጠበቅ ነው።
        """
        password = validated_data.pop('password')
        email = validated_data.get('email')
        name = validated_data.get('name')
        username = email.split('@')[0]

        with transaction.atomic():
            user = User.objects.create_user(username=username, email=email, password=password, first_name=name)
            
            request = self.context.get('request')
            if request and request.user:
                validated_data['created_by'] = request.user

            return Employee.objects.create(**validated_data)

# ==============================================================================
# SECTION 3: TASK MANAGEMENT
# ==============================================================================

class TaskSerializer(serializers.ModelSerializer):
    """
    የስራ መረጃዎችን ያሳያል። የSerializerMethodField አጠቃቀም ለዳታቤዝ ስሌቶች ጥሩ ነው።
    """
    assigned_to_details = EmployeeSerializer(source='assigned_to', read_only=True)
    created_by_details = UserMiniSerializer(source='created_by', read_only=True)
    day_left = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'status', 'due_date', 
                  'created_by', 'created_by_details', 'assigned_to', 
                  'assigned_to_details', 'created_at', 'updated_at', 'day_left']
        extra_kwargs = {
            'created_by': {'write_only': True, 'required': False},
            'assigned_to': {'write_only': True},
        }

    def get_day_left(self, obj):
        """የቀረውን ቀን የሚያሰላ ፈንክሽን።"""
        today = timezone.now().date()
        return (obj.due_date - today).days if obj.due_date > today else 0 

    def validate(self, data):
        """ርዕስ እና ማብራሪያ አንድ አይነት መሆን እንደሌለባቸው የሚያረጋግጥ የቢዝነስ ህግ።"""
        if data.get('title', '').lower() == data.get('description', '').lower():
            raise serializers.ValidationError("ርዕስ እና ማብራሪያ ተመሳሳይ መሆን አይችሉም።")
        return data