# urls.py
from django.urls import path

from . import views

urlpatterns = [
    path('csrf/', views.get_csrf_token, name='csrf_token'),
    path(
        'service-requests/create/',
        views.ServiceRequestCreateView.as_view(),
        name='service-request-create',
    ),
    path('guides/', views.GuideListView.as_view(), name='guide-list'),
    path(
        'guides/<slug:slug>/',
        views.GuideDetailView.as_view(),
        name='guide-detail',
    ),
    path('reviews/', views.UserReviewListView.as_view(), name='review-list'),
]
