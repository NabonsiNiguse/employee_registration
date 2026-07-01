# Serializers for the core appthise file data translation layer that serializes and deserializes data between complex data types (like Django models) and native Python data types, which can then be easily rendered into JSON or other content types. This is particularly useful for building RESTful APIs.
# this file used to translate python objects in to json formats and vice versa
from rest_fromework import serializers 
from django.contrib.auth.models import User
from.models import Employee, Task
#----------------
  # UserMiniSerializer
#-------------------
class UserMiniSerializers(serializers.modelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']
# ------------------------------------------------------------------------------
# 2. EmployeeSerializer (የሰራተኛ መረጃ ማጣሪያ እና መቀየሪያ)
# ----------------------------------------------
 class EmployeeSerializer(serializers.ModelSerializer):
    created_by_details = UserMiniSerializer(source='created_by', read_only=True)