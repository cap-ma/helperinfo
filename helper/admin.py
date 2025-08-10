from django.contrib import admin
from .models import (
    ServiceRequest,
    Guide,
    UserReview,
)

admin.site.register(
    [
        ServiceRequest,
        Guide,
        UserReview,
    ]
)
