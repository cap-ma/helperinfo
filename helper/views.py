from django.shortcuts import render

# Create your views here.
# views.py
from rest_framework import generics, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import timedelta

from .models import ServiceRequest, Guide, UserReview
from .serializers import (
    ServiceRequestSerializer,
    GuideListSerializer,
    GuideDetailSerializer,
    UserReviewSerializer,
)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 100


# Service Request Views
class ServiceRequestCreateView(generics.CreateAPIView):
    """Create a new service request"""

    queryset = ServiceRequest.objects.all()
    serializer_class = ServiceRequestSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        serializer.save()


# Helpful Guides Views
class GuideListView(generics.ListAPIView):
    """List all published helpful guides"""

    serializer_class = GuideListSerializer
    permission_classes = [AllowAny]
    pagination_class = StandardResultsSetPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ['category', 'is_featured']
    search_fields = ['title', 'short_description', 'content']
    ordering_fields = ['publication_date', 'view_count', 'title']
    ordering = ['-publication_date']

    def get_queryset(self):
        return Guide.objects.filter(is_published=True)


class GuideDetailView(generics.RetrieveAPIView):
    """Retrieve a specific helpful guide"""

    serializer_class = GuideDetailSerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'

    def get_queryset(self):
        return Guide.objects.filter(is_published=True)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Increment view count
        instance.increment_view_count()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


# User Reviews Views
class UserReviewListView(generics.ListAPIView):
    """List approved user reviews"""

    serializer_class = UserReviewSerializer
    permission_classes = [AllowAny]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['rating', 'service_used', 'is_verified']
    ordering_fields = ['created_at', 'rating', 'helpful_votes']
    ordering = ['-created_at']

    def get_queryset(self):
        return UserReview.objects.filter(is_approved=True)
