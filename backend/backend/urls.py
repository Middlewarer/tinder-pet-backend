from django.urls import path, include, re_path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView  # ← правильный импорт
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.contrib import admin

# Импорты твоих вьюх
from accounts.views import RegisterView, ProfileView
from animals.views import SwipeAnimalsView, OwnerAnimalDetailView, OwnerAnimalsListView
from interactions.views import LikeView, AcceptMatchView
from chats.views import MessageListView

schema_view = get_schema_view(
    openapi.Info(title="Tinder для животных API", default_version='v1'),
    public=True,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    # Swagger
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    # Auth
    path('api/auth/register/', RegisterView.as_view()),
    path('api/auth/login/', TokenObtainPairView.as_view()),
    path('api/auth/refresh/', TokenRefreshView.as_view()),
    path('api/profile/', ProfileView.as_view()),
    
    # Animals
    path('api/animals/swipe/', SwipeAnimalsView.as_view()),
    
    # Interactions
    path('api/like/', LikeView.as_view()),
    path('api/matches/<int:match_id>/accept/', AcceptMatchView.as_view()),
    
    # Chats
    path('api/chats/<int:chat_id>/messages/', MessageListView.as_view()),

    path('api/my-animals/', OwnerAnimalsListView.as_view(), name='my-animals'),
    path('api/my-animals/<int:pk>/', OwnerAnimalDetailView.as_view(), name='my-animal-detail'),
]