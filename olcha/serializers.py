from rest_framework import serializers
from olcha.models import (CategoryGroup, Category, Product,
                          ProductAttribute, CartItem, Cart,
                          Brand, Comment, Favorite)


class CategoryGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryGroup
        fields = '__all__'

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ProductAttributeSerializer(serializers.ModelSerializer):
    key = serializers.StringRelatedField()
    value = serializers.StringRelatedField()
    class Meta:
        model = ProductAttribute
        fields = ['key', 'value']

class ProductSerializer(serializers.ModelSerializer):
    final_price = serializers.SerializerMethodField()
    attributes = ProductAttributeSerializer(many=True, read_only=True)
    avg_rating = serializers.FloatField(read_only=True)

    def get_final_price(self, obj):
        return obj.final_price

    class Meta:
        model = Product
        fields = '__all__'


class CartItemSerializer(serializers.ModelSerializer):
    total_item_price = serializers.SerializerMethodField()

    def get_total_item_price(self, obj):
        return obj.total_item_price

    class Meta:
        model = CartItem
        fields = '__all__'

class CartSerializer(serializers.ModelSerializer):
    cart_items = CartItemSerializer(many=True, read_only=True)
    total_cart_price = serializers.SerializerMethodField()

    def get_total_cart_price(self, obj):
        return obj.total_cart_price

    class Meta:
        model = Cart
        fields = '__all__'

class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = '__all__'

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'

class AddToCartSerializer(serializers.Serializer):
    pk = serializers.IntegerField()
    quantity = serializers.IntegerField()


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = '__all__'
