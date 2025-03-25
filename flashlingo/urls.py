from django.contrib import admin
from django.urls import path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework_simplejwt import views as jwt_views

from game import views as game_views
from user import views as user_views

user_urls = [
    path(
        "api/token/", jwt_views.TokenObtainPairView.as_view(), name="token_obtain_pair"
    ),
    path(
        "api/token/refresh/",
        user_views.CustomTokenRefreshView.as_view(),
        name="token_refresh",
    ),
    path("register/", user_views.RegisterView.as_view(), name="register"),
    path("login/", user_views.LoginView.as_view(), name="login"),
    path("logout/", user_views.LogoutView.as_view(), name="logout"),
]
"""
    Game URLS
"""
game_urls = [
    path("admin/", admin.site.urls),
    path("dictionary/", game_views.GermanWordsView.as_view(), name="all_words"),
    path(
        "dictionary/<int:id>",
        game_views.GermanWordsByIdView.as_view(),
        name="words_by_id",
    ),
    path(
        "game-session/<int:id>",
        game_views.GetGameSessionView.as_view(),
        name="get_game_session",
    ),
    path(
        "game-session/update/<int:session_id>/",
        game_views.UpdateGameSessionView.as_view(),
        name="update_game_session",
    ),
    path(
        "all-session-stats",
        game_views.GetAllSessionStats.as_view(),
        name="get_all_session_stats",
    ),
]
"""
    Schema URLS
"""
schema_urls = [
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/schema/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
]

# Flatten the list of URL patterns
urlpatterns = user_urls + game_urls + schema_urls
