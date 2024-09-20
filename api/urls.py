from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

# Create a router and register the ChatbotViewSet
api_router = DefaultRouter()
api_router.register(r'chatbot', views.ChatbotViewSet, basename='chatbot')

urlpatterns = [
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('user/', views.UserDetailView.as_view(), name='user_detail'),
    path('token/', TokenObtainPairView.as_view(), name='get_token'),
    path('token/refresh/', TokenRefreshView.as_view(), name='refresh_token'),
    
    path('places/', views.PlaceListView.as_view(), name='place-list'),
    path('places/<int:id>/', views.PlaceDetailView.as_view(), name='place-detail'),
    path('like/<int:place_id>/', views.LikePlaceView.as_view(), name='like-place'),
    path('check-like/<int:placeid>/', views.check_place_liked, name='check_place_liked'),
    path('dislike-place/<int:placeid>/', views.dislike_place, name='dislike_place'),
    
    path('place-likes/<int:place_id>/', views.DisplayLikesView.as_view(), name='display-likes'),
    path('loved-places/', views.PlaceListView.as_view(), name='place-list'),
    # Include the router URLs here without an additional 'api/' prefix
    path('', include(api_router.urls)),
]
