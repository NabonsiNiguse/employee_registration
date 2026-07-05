from django.utils import timezone
from .models import Employee, Task
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken

# ==============================================================================
# 0. AdvancedLoginSerializer: ለሎግ-ኢን ማጣሪያ እና ቶከን ማመንጫ
# ==============================================================================
class AdvancedLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True, style={'input_type': 'password', 'placeholder': 'Password'})
      
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        # 1. ኢሜይል እና ፓስዎርድ መኖራቸውን ማረጋገጥ
        if not email or not password:
            raise serializers.ValidationError('Email and password are required.')
        
        # 2. ተጠቃሚውን በኢሜይል መፈለግ
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError('Invalid email or password.')
        
        # 3. ፓስዎርዱ ስህተት መሆኑን ማረጋገጥ
        if not user.check_password(password):
            raise serializers.ValidationError('Invalid email or password.')
        
        # 4. አካውንቱ መታገዱን (Active አለመሆኑን) ማረጋገጥ
        if not user.is_active:
            raise serializers.ValidationError('User account is not active.')
            
        # 5. ሁሉም ነገር ሰላም ከሆነ ቶከን ማመንጨት
        refresh_token = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh_token),
            'access': str(refresh_token.access_token),
            'username': user.username,
            'email': user.email,
            'message': 'Login successful.'
        }


# ==============================================================================
# 1. UserMiniSerializer: ለዩዘር መረጃ የሚያገለግል ቀለል ያለ ሴሪያላይዘር
# ==============================================================================
class UserMiniSerializer(serializers.ModelSerializer):
    """ዩዘርን ለሌሎች ሴሪያላይዘሮች እንደ 'read_only' መረጃ ለመጠቀም።"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


# ==============================================================================
# 2. EmployeeSerializer: የሰራተኛ መረጃ እና የሱ ስራዎች (Nested Data)
# ==============================================================================
class EmployeeSerializer(serializers.ModelSerializer):
    # 'source' በመጠቀም ከ User ሞዴል መረጃውን ይጎትታል
    created_by_details = UserMiniSerializer(source='created_by', read_only=True)
    
    # 'SerializerMethodField' ለዳታቤዝ ያልሆኑ የሂደት ውጤቶች
    task_assigned_to_details = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Employee
        fields = ['id', 'name', 'email', 'department', 'created_by', 'created_by_details', 'task_assigned_to_details']
        # 'created_by' ፊልድ ከFrontend ዳታ ሲቀበል ብቻ እንጂ ሲወጣ አይታይም
        extra_kwargs = {'created_by': {'write_only': True, 'required': False}}

    def get_task_assigned_to_details(self, obj):
        # Circular Import ለመፍታት ከፈንክሽኑ ውስጥ መጥራት (Advanced Practice)
        from .serializers import TaskSerializer
        # obj.assigned_tasks ማለት በሞዴሉ ላይ የተሰጠው related_name ነው
        tasks = obj.assigned_tasks.all() 
        return TaskSerializer(tasks, many=True).data

    def validate_email(self, value): 
        """የኢሜይል አድራሻን በአንድነት የሚፈትሽ Field-level validation"""
        if Employee.objects.filter(email=value).exists():
            raise serializers.ValidationError("ይህ ኢሜይል ቀድሞ ተመዝግቧል።")
        if not value.endswith('@gmail.com'):
            raise serializers.ValidationError("ኢሜይል የግድ '@gmail.com' መሆን አለበት።")
        return value


# ==============================================================================
# 3. TaskSerializer: የስራዎች መረጃ እና የጊዜ ስሌት (Complexity Level: High)
# ==============================================================================
class TaskSerializer(serializers.ModelSerializer):
    # Relational Fields: ለተጠቃሚው የሚታዩ (Read-only) ዝርዝር መረጃዎች
    assigned_to_details = EmployeeSerializer(source='assigned_to', read_only=True)
    created_by_details = UserMiniSerializer(source='created_by', read_only=True)
    
    # በቀን ስሌት የሚሰራ ዲናሚክ ፊልድ
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

    def get_day_left(self, obj):
        """የቀረውን ቀን የሚያሰላ ፈንክሽን - ከ Meta ውጪ መጻፍ አለበት!"""
        today = timezone.now().date()
        if obj.due_date > today:
            return (obj.due_date - today).days
        return 0 

    def validate(self, data):
        """Object-level validation: ከሁለት ፊልዶች በላይ ሲወዳደሩ"""
        title = data.get('title', '')
        description = data.get('description', '')
        # የቢዝነስ ህግ: ርዕስ እና ማብራሪያ አንድ አይነት መሆን አይችሉም
        if title.lower() == description.lower():
            raise serializers.ValidationError("ርዕስ እና ማብራሪያ ተመሳሳይ መሆን አይችሉም።")
        return data