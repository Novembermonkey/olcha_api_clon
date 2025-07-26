from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication

from olcha import permissions
from olcha.models import (
    CategoryGroup,
    Category,
    Product, Cart, CartItem, Brand, Comment)
from olcha.paginations import MyPagination
from olcha.serializers import CategoryGroupSerializer, CategorySerializer, ProductSerializer, CartSerializer, \
    BrandSerializer, CommentSerializer, AddToCartSerializer
from rest_framework import status
from rest_framework.response import Response
from django.db.models import Avg
from django.db.models.functions import Round
from collections import defaultdict
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend



# Create your views here.


class CategoryGroupViewSet(ModelViewSet):
    queryset = CategoryGroup.objects.all()
    serializer_class = CategoryGroupSerializer
    permission_classes = [permissions.IsStaffOrReadOnly]
    pagination_class = MyPagination
    lookup_field = 'slug'

    def list(self, request, *args, **kwargs):
        cache_key = "category_group_list"
        cached_data = cache.get(cache_key)

        if cached_data:
            return Response(cached_data)

        queryset = self.get_queryset()

        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data
        cache.set(cache_key, data, timeout=60)
        return Response(data)

    @method_decorator(cache_page(60))
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsStaffOrReadOnly]
    pagination_class = MyPagination
    lookup_field = 'slug'
    authorization_classes = [JWTAuthentication]

    def list(self, request, *args, **kwargs):
        cache_key = "catgory_list"
        cached_data = cache.get(cache_key)

        if cached_data:
            return Response(cached_data)

        queryset = self.get_queryset()

        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data
        cache.set(cache_key, data, timeout=60)
        return Response(data)

    @method_decorator(cache_page(60))
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)



class BrandViewSet(ModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = [permissions.IsStaffOrReadOnly]
    pagination_class = MyPagination
    lookup_field = 'slug'



    def retrieve(self, request, slug=None, *args, **kwargs):
        brand = get_object_or_404(Brand, slug=slug)

        products = Product.objects.filter(brand=brand) \
            .select_related('category') \
            .prefetch_related('attributes')

        grouped = defaultdict(list)
        for product in products:
            grouped[product.category.title].append(product)

        data = []
        for category_title, products_in_category in grouped.items():
            data.append({
                "category": category_title,
                "products": ProductSerializer(products_in_category, many=True).data
            })

        return Response({
            "brand": {
                "title": brand.title,
                "logo": brand.logo.url if brand.logo else None,
            },
            "data": data
        })

class ProductViewSet(ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsStaffOrReadOnly]
    pagination_class = MyPagination

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'brand', 'price']
    search_fields = ['title']
    ordering_fields = ['price', 'created_at', 'avg_rating']
    ordering = ['title']

    def get_queryset(self):
        queryset =  Product.objects.annotate(avg_rating=Round(Avg("comments__rating"), precision=2)).prefetch_related('attributes')
        return queryset

    def list(self, request, *args, **kwargs):
        filters = ['search', 'ordering', 'category', 'brand', 'price']
        is_filtered = any(param in request.query_params for param in filters)

        if is_filtered:
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)



        limit = request.query_params.get('limit', '')
        offset = request.query_params.get('offset', '')
        page = request.query_params.get('page', '')

        cache_key = f"product_list_limit_{limit}_offset_{offset}_page_{page}"
        cached_data = cache.get(cache_key)

        if cached_data:
            return Response(cached_data)

        queryset = self.get_queryset()

        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
        else:
            serializer = self.get_serializer(queryset, many=True)
            response = Response(serializer.data)


        cache.set(cache_key, response.data, timeout=60)
        return response

    @method_decorator(cache_page(60))
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

class CartViewSet(ModelViewSet):
    serializer_class = CartSerializer
    queryset = Cart.objects.none()#faqat o'zini cartini ko'ra oladi


    def get_cart(self, request):
        if request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=request.user)
        else:
            if not request.session.session_key:
                request.session.create()
            session_key = request.session.session_key
            cart, created = Cart.objects.get_or_create(guest_session_key=session_key)
        return cart

    def list(self, request, *args, **kwargs):
        cart = self.get_cart(request)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    @action(methods=['POST'], detail=False, serializer_class=AddToCartSerializer)
    def add_to_cart(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        pk = serializer.validated_data['pk']
        quantity = serializer.validated_data['quantity']

        cart = self.get_cart(request)
        product = get_object_or_404(Product, pk=pk)

        item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            item.quantity += quantity
        else:
            item.quantity = quantity
        item.save()


        return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)

    @action(methods=['DELETE'], detail=True, url_path='remove-product')
    def remove_from_cart(self, request, pk=None):
        cart = self.get_cart(request)
        item = get_object_or_404(CartItem, pk=pk, cart=cart)
        if not item:
            return Response(status=status.HTTP_404_NOT_FOUND)
        item.delete()
        return Response("Item removed successfully", status=status.HTTP_204_NO_CONTENT)

    @action(methods=['DELETE'], detail=False)
    def clear_cart(self, request, *args, **kwargs):
        cart = self.get_cart(request)
        cart.items.all().delete()
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['PATCH'], detail=True, url_path='update-product-quantity')
    def update_product_quantity(self, request, pk=None):
        cart = self.get_cart(request)
        item = get_object_or_404(CartItem, pk=pk, cart=cart)
        try:
            item.quantity = request.data.get('quantity')
        except (ValueError, TypeError):
            return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            item.save()
            return Response("Quantity updated successfully.", status=status.HTTP_200_OK)

class CommentsViewSet(ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.OwnsOrReadOnly]
    pagination_class = MyPagination


def homepage_url(request):
    return HttpResponse( "This is homepage url!  Enter '/admin' to access admin page, \n '/olcha' to access ecommerce, \n '/users' for profile  then /register,  /login, /logout ")

