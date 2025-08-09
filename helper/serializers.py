# serializers.py
from rest_framework import serializers
from .models import (
    ServiceRequest, 
    HelpfulGuide, 
    GuideSection, 
    UserReview, 
    FAQ, 
    ContactMessage
)


class ServiceRequestSerializer(serializers.ModelSerializer):
    """Serializer for service request form submissions"""
    
    class Meta:
        model = ServiceRequest
        fields = [
            'id', 'full_name', 'email_address', 'phone_number', 'country_code',
            'services_needed', 'location', 'estimated_budget', 
            'detailed_requirements', 'additional_information',
            'business_type', 'business_requirements', 'created_at', 'status'
        ]
        read_only_fields = ['id', 'created_at', 'status']
    
    def validate_services_needed(self, value):
        """Validate that services_needed is a proper JSON structure"""
        if not isinstance(value, list):
            raise serializers.ValidationError("Services must be provided as a list")
        
        for service in value:
            if not isinstance(service, dict) or 'name' not in service or 'price' not in service:
                raise serializers.ValidationError(
                    "Each service must have 'name' and 'price' fields"
                )
        
        return value


class ServiceRequestListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing service requests"""
    
    services_count = serializers.SerializerMethodField()
    total_estimated_cost = serializers.SerializerMethodField()
    
    class Meta:
        model = ServiceRequest
        fields = [
            'id', 'full_name', 'email_address', 'services_count',
            'total_estimated_cost', 'status', 'created_at'
        ]
    
    def get_services_count(self, obj):
        return len(obj.services_needed) if obj.services_needed else 0
    
    def get_total_estimated_cost(self, obj):
        if not obj.services_needed:
            return 0
        return sum(float(service.get('price', 0)) for service in obj.services_needed)


class GuideSectionSerializer(serializers.ModelSerializer):
    """Serializer for guide sections"""
    
    class Meta:
        model = GuideSection
        fields = ['id', 'title', 'content', 'order']


class HelpfulGuideListSerializer(serializers.ModelSerializer):
    """Serializer for listing helpful guides"""
    
    sections_count = serializers.SerializerMethodField()
    reading_time = serializers.SerializerMethodField()
    
    class Meta:
        model = HelpfulGuide
        fields = [
            'id', 'title', 'slug', 'category', 'short_description',
            'featured_image', 'is_featured', 'publication_date',
            'view_count', 'likes', 'sections_count', 'reading_time'
        ]
    
    def get_sections_count(self, obj):
        return obj.sections.count()
    
    def get_reading_time(self, obj):
        """Estimate reading time based on content length"""
        # Rough estimate: 200 words per minute
        word_count = len(obj.content.split()) + sum(
            len(section.content.split()) for section in obj.sections.all()
        )
        return max(1, word_count // 200)


class HelpfulGuideDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for individual guide view"""
    
    sections = GuideSectionSerializer(many=True, read_only=True)
    reading_time = serializers.SerializerMethodField()
    related_guides = serializers.SerializerMethodField()
    
    class Meta:
        model = HelpfulGuide
        fields = [
            'id', 'title', 'slug', 'category', 'short_description',
            'content', 'meta_description', 'keywords', 'featured_image',
            'is_featured', 'publication_date', 'view_count', 'likes',
            'sections', 'reading_time', 'related_guides', 'created_at', 'updated_at'
        ]
    
    def get_reading_time(self, obj):
        """Estimate reading time based on content length"""
        word_count = len(obj.content.split()) + sum(
            len(section.content.split()) for section in obj.sections.all()
        )
        return max(1, word_count // 200)
    
    def get_related_guides(self, obj):
        """Get related guides from the same category"""
        related = HelpfulGuide.objects.filter(
            category=obj.category,
            is_published=True
        ).exclude(id=obj.id)[:3]
        
        return HelpfulGuideListSerializer(related, many=True).data


class UserReviewSerializer(serializers.ModelSerializer):
    """Serializer for user reviews"""
    
    star_rating = serializers.ReadOnlyField()
    days_ago = serializers.SerializerMethodField()
    
    class Meta:
        model = UserReview
        fields = [
            'id', 'reviewer_name', 'reviewer_country', 'reviewer_avatar',
            'title', 'content', 'rating', 'star_rating', 'service_used',
            'is_verified', 'helpful_votes', 'days_ago', 'created_at'
        ]
        read_only_fields = ['id', 'helpful_votes', 'created_at']
    
    def get_days_ago(self, obj):
        """Calculate days since review was created"""
        from django.utils import timezone
        delta = timezone.now() - obj.created_at
        return delta.days


class UserReviewCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new reviews"""
    
    class Meta:
        model = UserReview
        fields = [
            'reviewer_name', 'reviewer_email', 'reviewer_country',
            'title', 'content', 'rating', 'service_used'
        ]
    
    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5")
        return value


class FAQSerializer(serializers.ModelSerializer):
    """Serializer for FAQ items"""
    
    class Meta:
        model = FAQ
        fields = [
            'id', 'question', 'answer', 'category', 'is_featured'
        ]


class ContactMessageSerializer(serializers.ModelSerializer):
    """Serializer for contact messages"""
    
    class Meta:
        model = ContactMessage
        fields = [
            'id', 'name', 'email', 'phone', 'subject', 'message', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class GuideStatsSerializer(serializers.Serializer):
    """Serializer for guide statistics"""
    
    total_guides = serializers.IntegerField()
    total_views = serializers.IntegerField()
    categories = serializers.DictField()
    most_popular = HelpfulGuideListSerializer()
    recent_guides = HelpfulGuideListSerializer(many=True)


class ReviewStatsSerializer(serializers.Serializer):
    """Serializer for review statistics"""
    
    total_reviews = serializers.IntegerField()
    average_rating = serializers.FloatField()
    rating_distribution = serializers.DictField()
    recent_reviews = UserReviewSerializer(many=True)


class ServiceRequestStatsSerializer(serializers.Serializer):
    """Serializer for service request statistics"""
    
    total_requests = serializers.IntegerField()
    pending_requests = serializers.IntegerField()
    completed_requests = serializers.IntegerField()
    popular_services = serializers.DictField()
    monthly_trend = serializers.ListField()