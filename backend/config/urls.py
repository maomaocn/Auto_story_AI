from django.contrib import admin
from django.urls import path, include, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view

# drf_yasg2 从这里开始
from rest_framework import permissions


schema_view = get_schema_view(
    openapi.Info(
        title="Auto Story API",
        default_version='v1',
        description="Welcome to the world of Auto Story API",
        # terms_of_service="https://www.tweet.org",
        # contact=openapi.Contact(email="demo@tweet.org"),
        # license=openapi.License(name="Awesome IP"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)
# 这里结束


urlpatterns = [
    re_path(r'^doc(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),  # <-- 这里
    path('doc/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),  # <-- 这里
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),  # <-- 这里
    path('admin/', admin.site.urls),
    path('user/', include('apps.users.urls')),
    path('models/', include('apps.models.urls')),
    # path('tasks/', include('apps.test.urls'))
]
