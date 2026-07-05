from rest_framework import viewsets, permissions, filters , status
from rest_framework.views import ApiView
from django.contrib.auth.models import User 
from .models import Employee, Task
from .serializers import EmployeeSerializer, TaskSerializer, UserMiniSerializer
from rest_framework_simplejwt.tokens import RefreshToken
  
  
class EmployeeViewSet(viewSet.ModelViewSet):
    serializer_class = EmployeeSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['department', 'created_by']
    search_fields = ['name', 'email']
      def get_queryset(self):
        user + self.rquests.user
        if user.is_staff and user_is_superuser:
            return Employee.objects.all()
        return Employee.objects.filter(email=user.email)

class EmployeeLoginView(ApiView):
   def post(self,request):
    email = request.data.get('email')
    password = request.data.get('password')
    if not email of not password:
      return Response({ "error": "please insert your email and password "}, status.status.HTTP_400_BAD_REQUEST)
    #check the email
    try:
    user = request.User.get(email=email) 
    except User.DoesNotExist:
      return Response({"error":"invalid email"}, status=status.HTTP_400_BAD_REQUEST)
      # check the pasword 
      if user.check_password(password):
         # give a token for user 
         refresh = RefreshToken.for_user(user)
         return Response({
          'refresh': str(refresh)
          'access': str(refresh.access_token),
          'message':'wellcome'
         }),status.status.HTTP_200_OK)
      return Response({"error":"your information is wrong"})status=status.HTTP_400_BAD_REQUEST)
         

    

    
