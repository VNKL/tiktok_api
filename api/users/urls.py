from django.urls import path
from rest_framework_jwt.views import obtain_jwt_token

from .views import *

app_name = 'users'

urlpatterns = [
    path('', UserIndexView.as_view()),
    path('.auth', obtain_jwt_token),
    path('.get', UserGetView.as_view()),    # extended
]
