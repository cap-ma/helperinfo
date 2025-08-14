# serializers.py
from rest_framework import serializers
from bs4 import BeautifulSoup
from .models import (
    ServiceRequest,
    Guide,
    UserReview,
)


# 1
class ServiceRequestSerializer(serializers.ModelSerializer):
    """Serializer for service request form submissions"""

    class Meta:
        model = ServiceRequest
        fields = [
            'id',
            'full_name',
            'email_address',
            'phone_number',
            'country_code',
            'services_needed',
            'location',
            'estimated_budget',
            'detailed_requirements',
            'additional_information',
            'business_type',
            'business_requirements',
            'created_at',
            'status',
        ]
        read_only_fields = ['id', 'created_at', 'status']

    def validate_services_needed(self, value):
        """Validate that services_needed is a proper JSON structure"""
        if not isinstance(value, list):
            raise serializers.ValidationError('Services must be provided as a list')

        for service in value:
            if (
                not isinstance(service, dict)
                or 'name' not in service
                or 'price' not in service
            ):
                raise serializers.ValidationError(
                    "Each service must have 'name' and 'price' fields"
                )

        return value


# 2
class GuideListSerializer(serializers.ModelSerializer):
    reading_time = serializers.SerializerMethodField()

    class Meta:
        model = Guide
        fields = [
            'id',
            'title',
            'slug',
            'category',
            'short_description',
            'featured_image',
            'is_featured',
            'publication_date',
            'view_count',
            'likes',
            'reading_time',
        ]

    def to_representation(self, instance):
        lang = self.context['request'].GET.get('lang')
        if lang:
            instance.set_current_language(lang)
        return super().to_representation(instance)

    def get_reading_time(self, obj):
        word_count = len((obj.content or '').split())
        return max(1, word_count // 200)


# 3
class GuideDetailSerializer(serializers.ModelSerializer):
    reading_time = serializers.SerializerMethodField()
    related_guides = serializers.SerializerMethodField()
    content = serializers.SerializerMethodField()

    class Meta:
        model = Guide
        fields = [
            'id',
            'title',
            'slug',
            'category',
            'short_description',
            'content',
            'meta_description',
            'keywords',
            'featured_image',
            'is_published',
            'is_featured',
            'publication_date',
            'view_count',
            'likes',
            'reading_time',
            'related_guides',
            'created_at',
            'updated_at',
        ]

    def to_representation(self, instance):
        lang = self.context['request'].GET.get('lang')
        if lang:
            print(lang)
            instance.set_current_language(lang)
        return super().to_representation(instance)

    def get_reading_time(self, obj):
        word_count = len((obj.content or '').split())
        return max(1, word_count // 200)

    def get_related_guides(self, obj):
        related = Guide.objects.filter(
            category=obj.category, is_published=True
        ).exclude(id=obj.id)[:3]
        return GuideListSerializer(related, many=True, context=self.context).data

    def get_content(self, obj):
        html = obj.content or ''
        request = self.context.get('request')
        if not request:
            return html

        soup = BeautifulSoup(html, 'html.parser')
        for img in soup.find_all('img'):
            src = img.get('src', '')
            if src.startswith('/'):
                img['src'] = request.build_absolute_uri(src)
        return str(soup)


# 4
class UserReviewSerializer(serializers.ModelSerializer):
    """Serializer for user reviews"""

    star_rating = serializers.ReadOnlyField()
    days_ago = serializers.SerializerMethodField()

    class Meta:
        model = UserReview
        fields = [
            'id',
            'reviewer_name',
            'reviewer_country',
            'reviewer_avatar',
            'title',
            'content',
            'rating',
            'star_rating',
            'service_used',
            'is_verified',
            'helpful_votes',
            'days_ago',
            'created_at',
        ]
        read_only_fields = ['id', 'helpful_votes', 'created_at']

    def get_days_ago(self, obj):
        """Calculate days since review was created"""
        from django.utils import timezone

        delta = timezone.now() - obj.created_at
        return delta.days
