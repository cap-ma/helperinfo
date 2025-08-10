from ckeditor_uploader.fields import RichTextUploadingField


from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


class ServiceRequest(models.Model):
    """Model for service request form submissions"""

    SERVICE_CHOICES = [
        ('wi_fi_sim_setup', 'Wi-Fi & SIM Setup'),
        ('apartment_finding', 'Apartment Finding'),
        ('grocery_help', 'Grocery Help'),
        ('translation_services', 'Translation Services'),
        ('bill_payments', 'Bill Payments'),
        ('transportation_help', 'Transportation Help'),
        ('document_assistance', 'Document Assistance'),
        ('social_integration', 'Social Integration'),
        ('business_support', 'Business Support'),
        ('healthcare_navigation', 'Healthcare Navigation'),
        ('food_dining', 'Food & Dining'),
        ('customs_request', 'Customs Request'),
    ]

    # Personal Information
    full_name = models.CharField(max_length=100)
    email_address = models.EmailField()
    phone_number = models.CharField(max_length=20)
    country_code = models.CharField(max_length=5, default='+998')

    # Service Selection
    services_needed = models.JSONField(
        help_text='List of selected services with their prices'
    )

    # Location & Budget
    location = models.CharField(max_length=200, blank=True, null=True)
    estimated_budget = models.CharField(max_length=50, blank=True, null=True)

    # Request Details
    detailed_requirements = models.TextField(
        help_text='Detailed description of requirements'
    )

    # Additional Information
    additional_information = models.TextField(blank=True, null=True)

    # Business Information (Optional)
    business_type = models.CharField(max_length=100, blank=True, null=True)
    business_requirements = models.TextField(blank=True, null=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_processed = models.BooleanField(default=False)
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('in_progress', 'In Progress'),
            ('completed', 'Completed'),
            ('cancelled', 'Cancelled'),
        ],
        default='pending',
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Service Request'
        verbose_name_plural = 'Service Requests'

    def __str__(self):
        return f'{self.full_name} - {self.created_at.strftime("%Y-%m-%d")}'


class Guide(models.Model):
    """Model for helpful guides section"""

    GUIDE_CATEGORIES = [
        ('banking_finance', 'Banking & Finance'),
        ('transportation', 'Transportation'),
        ('documentation', 'Documentation'),
        ('housing', 'Housing & Accommodation'),
        ('healthcare', 'Healthcare'),
        ('business', 'Business & Legal'),
        ('cultural', 'Cultural Integration'),
        ('emergency', 'Emergency Services'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    category = models.CharField(max_length=30, choices=GUIDE_CATEGORIES)
    short_description = models.TextField(max_length=300)
    content = RichTextUploadingField(
        help_text='Detailed guide content with rich text formatting'
    )

    # SEO and Meta
    meta_description = models.CharField(max_length=160, blank=True, null=True)
    keywords = models.CharField(max_length=200, blank=True, null=True)

    # Featured image
    featured_image = models.ImageField(
        upload_to='guides/images/',
        blank=True,
        null=True,
        help_text='Featured image for the guide',
    )

    # Publishing
    is_published = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    publication_date = models.DateTimeField(default=timezone.now)

    # Engagement metrics
    view_count = models.PositiveIntegerField(default=0)
    likes = models.PositiveIntegerField(default=0)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-publication_date']
        verbose_name = 'Guide'
        verbose_name_plural = 'Guides'

    def __str__(self):
        return self.title

    def increment_view_count(self):
        """Increment view count when guide is accessed"""
        self.view_count += 1
        self.save(update_fields=['view_count'])


class UserReview(models.Model):
    """Model for user reviews and testimonials"""

    RATING_CHOICES = [(i, i) for i in range(1, 6)]  # 1-5 star rating

    # Reviewer Information
    reviewer_name = models.CharField(max_length=100)
    reviewer_email = models.EmailField(blank=True, null=True)
    reviewer_country = models.CharField(max_length=50, blank=True, null=True)
    reviewer_avatar = models.ImageField(
        upload_to='reviews/avatars/', blank=True, null=True
    )

    # Review Content
    title = models.CharField(max_length=200, blank=True, null=True)
    content = models.TextField(max_length=1000)
    rating = models.IntegerField(
        choices=RATING_CHOICES, validators=[MinValueValidator(1), MaxValueValidator(5)]
    )

    # Service Related
    service_used = models.CharField(
        max_length=50, choices=ServiceRequest.SERVICE_CHOICES, blank=True, null=True
    )

    # Review Status
    is_approved = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)

    # Engagement
    helpful_votes = models.PositiveIntegerField(default=0)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'User Review'
        verbose_name_plural = 'User Reviews'

    def __str__(self):
        return f'{self.reviewer_name} - {self.rating} stars'

    @property
    def star_rating(self):
        """Return rating as star display"""
        return self.rating
