import asyncio

import httpx
from django.conf import settings
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.utils import translation
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods
from django_filters.rest_framework import DjangoFilterBackend

# Create your views here.
# views.py
from rest_framework import filters, generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import Guide, ServiceRequest, UserReview
from .serializers import (
    GuideDetailSerializer,
    GuideListSerializer,
    ServiceRequestSerializer,
    UserReviewSerializer,
)

CHAT_ID = settings.CHAT_ID
BOT_TOKEN = settings.BOT_TOKEN


async def send_telegram_message(text: str):
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
    payload = {'chat_id': CHAT_ID, 'text': text}

    async with httpx.AsyncClient() as client:
        await client.post(url, data=payload)


@ensure_csrf_cookie
@require_http_methods(['GET'])
def get_csrf_token(request):
    """
    Get CSRF token for the client
    """
    token = get_token(request)
    return JsonResponse({'csrfToken': token, 'success': True})


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
        instance = serializer.save()

        service_text = '\n\n'
        for service in instance.services_needed:
            name = service.get('name', '')
            price = service.get('price', '')
            service_text += f'🔹 {name}: {price}\n'

        message = (
            f'📩 New Submission\n\n'
            f'👤 Full Name: {instance.full_name}\n'
            f'📧 Email: {instance.email_address}\n'
            f'📱 Phone: {instance.phone_number}\n'
            f'🏳️ Country Code: {instance.country_code}\n'
            f'🛠️ Services Needed: {service_text}\n'
            f'📍 Location: {instance.location}\n'
            f'💰 Estimated Budget: {instance.estimated_budget}\n'
            f'📜 Detailed Requirements: {instance.detailed_requirements}\n'
            f'📝 Additional Info: {instance.additional_information}\n'
            f'🏢 Business Type: {instance.business_type}\n'
            f'📋 Business Requirements: {instance.business_requirements}\n'
            f'🕒 Created At: {instance.created_at}\n'
            f'♻️ Updated At: {instance.updated_at}\n'
            f'✅ Processed: {instance.is_processed}\n'
            f'📌 Status: {instance.status}'
        )

        # Send Telegram notification
        asyncio.run(send_telegram_message(message))


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

    def initial(self, request, *args, **kwargs):
        lang = request.GET.get('lang')
        if lang:
            translation.activate(lang)
        return super().initial(request, *args, **kwargs)

    def get_queryset(self):
        return Guide.objects.filter(is_published=True)


class GuideDetailView(generics.RetrieveAPIView):
    """Retrieve a specific helpful guide"""

    serializer_class = GuideDetailSerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'

    def initial(self, request, *args, **kwargs):
        lang = request.GET.get('lang')
        if lang:
            translation.activate(lang)
        return super().initial(request, *args, **kwargs)

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
