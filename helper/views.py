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

from .models import (
    ServiceRequest, 
    HelpfulGuide, 
    UserReview, 
    FAQ, 
    ContactMessage
)
from .serializers import (
    ServiceRequestSerializer,
    ServiceRequestListSerializer,
    HelpfulGuideListSerializer,
    HelpfulGuideDetailSerializer,
    UserReviewSerializer,
    UserReviewCreateSerializer,
    FAQSerializer,
    ContactMessageSerializer,
    GuideStatsSerializer,
    ReviewStatsSerializer,
    ServiceRequestStatsSerializer
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


class ServiceRequestListView(generics.ListAPIView):
    """List all service requests (admin only)"""
    queryset = ServiceRequest.objects.all()
    serializer_class = ServiceRequestListSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'created_at']
    search_fields = ['full_name', 'email_address']
    ordering_fields = ['created_at', 'full_name']
    ordering = ['-created_at']


class ServiceRequestDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a service request"""
    queryset = ServiceRequest.objects.all()
    serializer_class = ServiceRequestSerializer


# Helpful Guides Views
class HelpfulGuideListView(generics.ListAPIView):
    """List all published helpful guides"""
    serializer_class = HelpfulGuideListSerializer
    permission_classes = [AllowAny]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_featured']
    search_fields = ['title', 'short_description', 'content']
    ordering_fields = ['publication_date', 'view_count', 'title']
    ordering = ['-publication_date']
    
    def get_queryset(self):
        return HelpfulGuide.objects.filter(is_published=True)


class HelpfulGuideDetailView(generics.RetrieveAPIView):
    """Retrieve a specific helpful guide"""
    serializer_class = HelpfulGuideDetailSerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'
    
    def get_queryset(self):
        return HelpfulGuide.objects.filter(is_published=True)
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Increment view count
        instance.increment_view_count()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class FeaturedGuidesView(generics.ListAPIView):
    """Get featured guides"""
    serializer_class = HelpfulGuideListSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        return HelpfulGuide.objects.filter(
            is_published=True, 
            is_featured=True
        )[:6]


class PopularGuidesView(generics.ListAPIView):
    """Get most popular guides by view count"""
    serializer_class = HelpfulGuideListSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        return HelpfulGuide.objects.filter(
            is_published=True
        ).order_by('-view_count')[:6]


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


class UserReviewCreateView(generics.CreateAPIView):
    """Create a new user review"""
    queryset = UserReview.objects.all()
    serializer_class = UserReviewCreateSerializer
    permission_classes = [AllowAny]


class FeaturedReviewsView(generics.ListAPIView):
    """Get featured reviews for homepage"""
    serializer_class = UserReviewSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        return UserReview.objects.filter(
            is_approved=True,
            is_featured=True
        )[:6]


# FAQ Views
class FAQListView(generics.ListAPIView):
    """List all FAQs"""
    queryset = FAQ.objects.all()
    serializer_class = FAQSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category', 'is_featured']


# Contact Views
class ContactMessageCreateView(generics.CreateAPIView):
    """Create a contact message"""
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer
    permission_classes = [AllowAny]


# Statistics and Dashboard Views
@api_view(['GET'])
@permission_classes([AllowAny])
def guide_statistics(request):
    """Get guide statistics"""
    guides = HelpfulGuide.objects.filter(is_published=True)
    
    # Category statistics
    categories = dict(guides.values_list('category', flat=True).annotate(
        count=Count('category')
    ))
    
    # Most popular guide
    most_popular = guides.order_by('-view_count').first()
    
    # Recent guides
    recent_guides = guides.order_by('-publication_date')[:5]
    
    stats = {
        'total_guides': guides.count(),
        'total_views': sum(guides.values_list('view_count', flat=True)),
        'categories': categories,
        'most_popular': HelpfulGuideListSerializer(most_popular).data if most_popular else None,
        'recent_guides': HelpfulGuideListSerializer(recent_guides, many=True).data
    }
    
    serializer = GuideStatsSerializer(stats)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def review_statistics(request):
    """Get review statistics"""
    reviews = UserReview.objects.filter(is_approved=True)
    
    # Rating distribution
    rating_distribution = {}
    for i in range(1, 6):
        rating_distribution[str(i)] = reviews.filter(rating=i).count()
    
    # Recent reviews
    recent_reviews = reviews.order_by('-created_at')[:5]
    
    stats = {
        'total_reviews': reviews.count(),
        'average_rating': reviews.aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0,
        'rating_distribution': rating_distribution,
        'recent_reviews': UserReviewSerializer(recent_reviews, many=True).data
    }
    
    serializer = ReviewStatsSerializer(stats)
    return Response(serializer.data)


@api_view(['GET'])
def service_request_statistics(request):
    """Get service request statistics (admin only)"""
    requests = ServiceRequest.objects.all()
    
    # Status counts
    pending = requests.filter(status='pending').count()
    completed = requests.filter(status='completed').count()
    
    # Popular services (extract from JSON field)
    popular_services = {}
    for req in requests:
        if req.services_needed:
            for service in req.services_needed:
                service_name = service.get('name', 'Unknown')
                popular_services[service_name] = popular_services.get(service_name, 0) + 1
    
    # Monthly trend (last 12 months)
    monthly_trend = []
    for i in range(12):
        date = timezone.now() - timedelta(days=i*30)
        count = requests.filter(
            created_at__year=date.year,
            created_at__month=date.month
        ).count()
        monthly_trend.append({
            'month': date.strftime('%B %Y'),
            'count': count
        })
    
    stats = {
        'total_requests': requests.count(),
        'pending_requests': pending,
        'completed_requests': completed,
        'popular_services': popular_services,
        'monthly_trend': monthly_trend
    }
    
    serializer = ServiceRequestStatsSerializer(stats)
    return Response(serializer.data)


# Search Views
@api_view(['GET'])
@permission_classes([AllowAny])
def search_content(request):
    """Search across guides, FAQs, and reviews"""
    query = request.GET.get('q', '')
    
    if not query:
        return Response({
            'guides': [],
            'faqs': [],
            'reviews': []
        })
    
    # Search guides
    guides = HelpfulGuide.objects.filter(
        Q(title__icontains=query) | 
        Q(short_description__icontains=query) |
        Q(content__icontains=query),
        is_published=True
    )[:5]
    
    # Search FAQs
    faqs = FAQ.objects.filter(
        Q(question__icontains=query) | 
        Q(answer__icontains=query)
    )[:5]
    
    # Search reviews
    reviews = UserReview.objects.filter(
        Q(title__icontains=query) |
        Q(content__icontains=query),
        is_approved=True
    )[:5]
    
    return Response({
        'guides': HelpfulGuideListSerializer(guides, many=True).data,
        'faqs': FAQSerializer(faqs, many=True).data,
        'reviews': UserReviewSerializer(reviews, many=True).data
    })


# Utility Views
@api_view(['POST'])
@permission_classes([AllowAny])
def like_guide(request, guide_id):
    """Like a guide"""
    try:
        guide = HelpfulGuide.objects.get(id=guide_id, is_published=True)
        guide.likes += 1
        guide.save(update_fields=['likes'])
        return Response({'likes': guide.likes})
    except HelpfulGuide.DoesNotExist:
        return Response(
            {'error': 'Guide not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def helpful_review(request, review_id):
    """Mark a review as helpful"""
    try:
        review = UserReview.objects.get(id=review_id, is_approved=True)
        review.helpful_votes += 1
        review.save(update_fields=['helpful_votes'])
        return Response({'helpful_votes': review.helpful_votes})
    except UserReview.DoesNotExist:
        return Response(
            {'error': 'Review not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )