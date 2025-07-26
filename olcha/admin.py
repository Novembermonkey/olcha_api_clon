from django.contrib import admin

from olcha.models import (CategoryGroup, Category,
                          Product, ProductAttribute, AttributeKey, AttributeValue, Favorite,
                          Comment, Cart, CartItem)

# Register your models here.

models = [CategoryGroup, Category, Product, ProductAttribute, AttributeKey, AttributeValue,
          Comment, Favorite, Cart, CartItem]
admin.site.register(models)