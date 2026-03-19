"""
Root URL configuration with Swagger documentation.

Two doc UIs available:
- /swagger/ → interactive (try endpoints directly in browser)
- /redoc/   → clean readable format
"""

from django.contrib import admin
from django.urls import path, include, re_path
from django.http import JsonResponse
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# --- Swagger Schema Setup ---
schema_view = get_schema_view(
    openapi.Info(
        title='AI Quiz API',
        default_version='v1',
        description='''
## AI-Powered Quiz API

A RESTful API for creating and taking AI-generated quizzes.

### Authentication
Use JWT Bearer tokens. Get your token from `/api/auth/login/`.

Add to headers: `Authorization: Bearer <your_token>`

### Roles
- **student** → can browse and attempt quizzes
- **admin**   → can create, publish, and manage quizzes
        ''',
        contact=openapi.Contact(email='admin@quizapi.com'),
        license=openapi.License(name='MIT License'),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)


def health_check(request):
    """Server health check endpoint."""
    return JsonResponse({
        'status': 'healthy',
        'version': '1.0.0',
        'service': 'Quiz API'
    })


urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Health check
    path('health/', health_check, name='health-check'),

    # API docs
    re_path(
        r'^swagger(?P<format>\.json|\.yaml)$',
        schema_view.without_ui(cache_timeout=0),
        name='schema-json'
    ),
    path(
        'swagger/',
        schema_view.with_ui('swagger', cache_timeout=0),
        name='schema-swagger-ui'
    ),
    path(
        'redoc/',
        schema_view.with_ui('redoc', cache_timeout=0),
        name='schema-redoc'
    ),

    # API v1
    path('api/', include([
        path('auth/', include('users.urls')),
        path('quizzes/', include('quizzes.urls')),
        path('attempts/', include('attempts.urls')),
        path('analytics/', include('analytics.urls')),
    ])),
]