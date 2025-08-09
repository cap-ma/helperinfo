# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views


urlpatterns = [

    path('api/service-requests/create/', views.ServiceRequestCreateView.as_view(), name='service-request-create'),
    
    path('api/guides/', views.HelpfulGuideListView.as_view(), name='guide-list'),
    path('api/guides/<slug:slug>/', views.HelpfulGuideDetailView.as_view(), name='guide-detail'),

    path('api/reviews/', views.UserReviewListView.as_view(), name='review-list'),

    

]
