from django.urls import path, include, re_path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from accounts.views import RegisterView, ProfileView, PreferenceView, TagListView
from animals.views import SwipeAnimalsView, OwnerAnimalsListView, OwnerAnimalDetailView
from animals.views import CreateAnimalView, UpdateAnimalView, DeleteAnimalView
from interactions.views import LikeView, AcceptMatchView, PendingMatchesView
from interactions.views import AcceptedMatchesView, RejectMatchView, SentLikesView, ReceivedLikesView
from chats.views import MessageListView, ChatListView, ChatDetailView, ChatDeleteView

from django.contrib import admin

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
    path('api/auth/register/', RegisterView.as_view(), name='register'),
    path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/profile/', ProfileView.as_view(), name='profile'),
    
    # Preferences & Tags
    path('api/preferences/', PreferenceView.as_view(), name='preferences'),
    path('api/tags/', TagListView.as_view(), name='tags'),
    
    # Animals (для всех)
    path('api/animals/swipe/', SwipeAnimalsView.as_view(), name='swipe-animals'),
    
    # Animals (для владельца)
    path('api/my-animals/', OwnerAnimalsListView.as_view(), name='my-animals'),
    path('api/my-animals/<int:pk>/', OwnerAnimalDetailView.as_view(), name='my-animal-detail'),
    path('api/animals/create/', CreateAnimalView.as_view(), name='create-animal'),
    path('api/animals/<int:pk>/update/', UpdateAnimalView.as_view(), name='update-animal'),
    path('api/animals/<int:pk>/delete/', DeleteAnimalView.as_view(), name='delete-animal'),
    
    # Likes & Matches
    path('api/like/', LikeView.as_view(), name='like'),
    path('api/likes/sent/', SentLikesView.as_view(), name='sent-likes'),
    path('api/likes/received/', ReceivedLikesView.as_view(), name='received-likes'),
    
    # Matches (для владельца)
    path('api/matches/pending/', PendingMatchesView.as_view(), name='pending-matches'),
    path('api/matches/accepted/', AcceptedMatchesView.as_view(), name='accepted-matches'),
    path('api/matches/<int:match_id>/accept/', AcceptMatchView.as_view(), name='accept-match'),
    path('api/matches/<int:match_id>/reject/', RejectMatchView.as_view(), name='reject-match'),
    
    # Chats
    path('api/chats/', ChatListView.as_view(), name='chat-list'),
    path('api/chats/<int:pk>/', ChatDetailView.as_view(), name='chat-detail'),
    path('api/chats/<int:pk>/delete/', ChatDeleteView.as_view(), name='chat-delete'),
    path('api/chats/<int:chat_id>/messages/', MessageListView.as_view(), name='chat-messages'),
]