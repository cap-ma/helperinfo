from django.contrib import admin
from parler.admin import TranslatableAdmin

from .models import (
    Guide,
    ServiceRequest,
    UserReview,
)

admin.site.register(
    [
        ServiceRequest,
        UserReview,
    ]
)


@admin.register(Guide)
class GuideAdmin(TranslatableAdmin):
    list_display = ('title', 'category', 'is_published', 'publication_date')
    search_fields = ('title',)
    readonly_fields = ('slug',)
