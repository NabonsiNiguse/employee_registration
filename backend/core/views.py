from rest_framework import viewsets, permissions, filters, status
from rest_framework.views import APIView  # APIView በትልቁ ተስተካክሏል
from rest_framework.response import Response  # የጎደለው ሪስፖንስ ተጨምሯል
from django_filters.rest_framework import DjangoFilterBackend  # የጎደለው ፊልተር ተጨምሯል
from django.contrib.auth.models import User 
from .models import Employee, Task
from .serializers import EmployeeSerializer, TaskSerializer, AdvancedLoginSerializer, UserMiniSerializer

class EmployeeViewSet(viewsets.ModelViewSet):  # viewsets በትንሹ ተስተካክሏል
    serializer_class = EmployeeSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['department', 'created_by']
    search_fields = ['name', 'email']

    def get_queryset(self):
        user = self.request.user  # የፊደል ግድፈቱ (+ እና rquests) ተስተካክሏል
        # ለአስተዳዳሪዎች ሁሉንም፣ ለተራ ሰራተኛ የራሱን ብቻ ማሳያ ሎጂክ
        if user.is_staff or user.is_superuser:  # user.is_superuser ተስተካክሏል
            return Employee.objects.all()
        return Employee.objects.filter(email=user.email)

class AdvancedLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    # የሎግ-ኢን ሎጂኩ ወደ POST ዘዴ (Method) ተዛውሯል
    def post(self, request):
        serializer = AdvancedLoginSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)