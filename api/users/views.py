from django.shortcuts import get_object_or_404
from rest_framework import views, status
from rest_framework import permissions
from rest_framework.response import Response

from .serializers import *
from .models import User


class UserIndexView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response({'error': 'Use users methods'},
                        status=status.HTTP_405_METHOD_NOT_ALLOWED)


class UserGetView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = get_object_or_404(User, username=request.user.username)
        serializer = UserSerializer(user)
        return Response(serializer.data)
