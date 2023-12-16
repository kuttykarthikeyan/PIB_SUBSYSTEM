from rest_framework import serializers
from .models import *

class news_cluster_head_serializer(serializers.ModelSerializer):
   
    class Meta:
        model = news_cluster_head
        fields =  '__all__'
        
class news_obj_serializer(serializers.ModelSerializer):
    class Meta:
        model = news_obj
        fields =  '__all__'