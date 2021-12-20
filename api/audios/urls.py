from django.urls import path

from .views import *

app_name = 'audios'

urlpatterns = [
    path('', AudiosIndexView.as_view()),
    path('.add', AudiosAddView.as_view()),
    path('.get', AudiosGetView.as_view()),
    path('.getAll', AudiosGetAllView.as_view({'get': 'list'})),
    path('.getLiked', AudiosGetLikedView.as_view({'get': 'list'})),
    path('.getOwned', AudiosGetOwnedView.as_view({'get': 'list'})),
    path('.getAbsoluteChart', AbsoluteChartView.as_view({'get': 'list'})),
    path('.getPercentChart', PercentChartView.as_view({'get': 'list'})),
    path('.like', AudiosLikeView.as_view({'get': 'list'})),
    path('.parsTrends', AudiosParsTrendsView.as_view()),
    path('.updateStats', AudiosUpdateStatsView.as_view()),
]
