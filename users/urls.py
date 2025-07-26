from django.urls import path, include
from users import views
from rest_framework_simplejwt.views import TokenRefreshView
from users.views import LogOutView, LogInView, RegisterView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

router.register(r'profiles', views.ProfileViewSet, basename='profiles')

app_name = 'users'

urlpatterns = [
            path('register/', RegisterView.as_view(), name='register'),
            path('login/', LogInView.as_view(), name='login'),
            path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
            path('logout/', LogOutView.as_view(), name='logout'),
            path('', include(router.urls)),
]