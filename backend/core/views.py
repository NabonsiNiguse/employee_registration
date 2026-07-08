from rest_framework import viewsets, permissions, filters, status
from rest_framework.views import APIView 
from rest_framework.response import Response 
from django_filters.rest_framework import DjangoFilterBackend 
from django.contrib.auth.models import User 
from .models import Employee, Task
from .serializers import EmployeeSerializer, TaskSerializer, AdvancedLoginSerializer

# ==============================================================================
# 1. EMPLOYEE VIEWSET (ModelViewSet አጠቃቀም)
# ==============================================================================
class EmployeeViewSet(viewsets.ModelViewSet):
    """
    ሰራተኞችን ለመፍጠር፣ ለማንበብ፣ ለማስተካከል እና ለመሰረዝ።
    IsAuthenticated በመሆኑ የገቡ ተጠቃሚዎች ብቻ ናቸው ማየት የሚችሉት።
    """
    serializer_class = EmployeeSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    # Filtering: የፍለጋ እና የፊልተር አቅም መጨመር
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['department', 'created_by']
    search_fields = ['user__first_name', 'user__email'] # 'name'ን 'user__first_name' ቀይረነዋል

    def get_queryset(self):
        """አድሚን ሁሉንም፣ ሰራተኛ ደግሞ የራሱን ፕሮፋይል ብቻ እንዲያይ የሚያደርግ ሎጂክ"""
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return Employee.objects.all()
        # Employee ሞዴል user ጋር OneToOne ስለሆነ፣ በቀጥታ ከ user ጋር ማጣራት ይሻላል
        return Employee.objects.filter(user=user)

# ==============================================================================
# 2. AUTHENTICATION VIEW (APIView አጠቃቀም)
# ==============================================================================
class AdvancedLoginView(APIView):
    """
    የተጠቃሚ መግቢያ (Login)።
    AllowAny በመሆኑ መግባት ያልቻሉ ሰዎችም ይህን ማግኘት ይችላሉ።
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """Login መረጃን ተቀብሎ ቶከን የሚመልስ POST ዘዴ"""
        serializer = AdvancedLoginSerializer(data=request.data)
        
        # የሴሪያላይዘር ቫሊዴሽን ከተሳካ ቶከኑን ይመልሳል
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        
        # ካልተሳካ የኤረር መልዕክቱን ይመልሳል
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)