from django.urls import path, include
from rest_framework import routers
from olcha.views import CategoryGroupViewSet, CategoryViewSet, ProductViewSet, CartViewSet, CommentsViewSet, \
    BrandViewSet

app_name = 'olcha'

router = routers.DefaultRouter()
router.register(r'category-groups', CategoryGroupViewSet, basename='category-groups')
router.register(r'categories', CategoryViewSet, basename='categories')
router.register(r'brands', BrandViewSet, basename='brands')
router.register(r'products', ProductViewSet, basename='products')
router.register(r'cart', CartViewSet, basename='cart')
router.register(r'comments', CommentsViewSet, basename='comments')


urlpatterns = [
            path('', include(router.urls)),
]