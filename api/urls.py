from django.urls import include, path
# import routers
from rest_framework import routers
 
# import everything from views
from .views import *

router = routers.DefaultRouter()

app_name = 'api'


urlpatterns = [
    path('', include(router.urls)),
    
]