from multiprocessing import Process

from django import db
from django.core.management import call_command
from django.utils.timezone import now
from rest_framework import views, viewsets, status
from rest_framework import permissions
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response

from .serializers import *
from .models import *
from .utils import process_like, get_sp_all_audios_with_likes, get_sp_liked_audios, get_sp_owned_audios
from api.users.permissions import UpdateStatsPermission, ParsTrendsPermission


class AudiosIndexView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response({'error': 'Use audios methods'},
                        status=status.HTTP_405_METHOD_NOT_ALLOWED)


class AudiosGetView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = AudioIDViewSerializer(data=request.query_params)
        if serializer.is_valid():
            audio = Audio.objects.filter(audio_id=serializer.data['audio_id']).first()
            serializer = AudioExtendedSerializer(audio)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AudiosGetAllView(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AudioLikedSerializer
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        return get_sp_all_audios_with_likes(query_params=self.request.query_params, user_id=self.request.user.id)


class AbsoluteChartView(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ChartSerializer
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        today = now().date()
        return AudioStat.objects.filter(date=today, count_delta__isnull=False).exclude(count_delta=0).order_by('-count_delta')


class PercentChartView(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ChartSerializer
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        today = now().date()
        return AudioStat.objects.filter(date=today, count_delta__isnull=False).exclude(count_delta=0).order_by('-count_delta_percent')


class AudiosGetLikedView(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AudioLikedSerializer
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        return get_sp_liked_audios(query_params=self.request.query_params, user_id=self.request.user.id)


class AudiosGetOwnedView(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AudioLikedSerializer
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        return get_sp_owned_audios(query_params=self.request.query_params, user_id=self.request.user.id)


class AudiosAddView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = AudioAddViewSerializer(data=request.query_params)
        if serializer.is_valid():
            data = {'tiktok_url': serializer.data['tiktok_url'], 'owner_username': request.user.username}
            db.connections.close_all()
            process = Process(target=call_command, args=('add_one_audio',), kwargs=data)
            process.start()
            return Response({'response': 'Parsing staring in background'}, status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AudiosLikeView(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AudioSerializer
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        serializer = AudioIDViewSerializer(data=self.request.query_params)
        if serializer.is_valid():
            process_like(audio_id=serializer.data['audio_id'], username=self.request.user.username)
        likes = AudioLike.objects.filter(user=self.request.user.id)
        return Audio.objects.filter(likes__in=likes).order_by('-add_date')


class AudiosParsTrendsView(views.APIView):
    permission_classes = [permissions.IsAuthenticated, ParsTrendsPermission]

    def get(self, request):
        serializer = ParsTrendsViewSerializer(data=request.query_params)
        if serializer.is_valid():
            db.connections.close_all()
            process = Process(target=call_command, args=('pars_trends',), kwargs=serializer.data)
            process.start()
            return Response({'response': 'Parsing staring in background'}, status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AudiosUpdateStatsView(views.APIView):
    permission_classes = [permissions.IsAuthenticated, UpdateStatsPermission]

    def get(self, request):
        db.connections.close_all()
        process = Process(target=call_command, args=('update_audio_stats',))
        process.start()
        return Response({'response': 'Updating stats staring in background'}, status.HTTP_200_OK)
