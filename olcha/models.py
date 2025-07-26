from django.db import models
from decimal import Decimal
from django.db.models import ForeignKey, Choices
from django.utils.text import slugify
from users.models import CustomUser


# Create your models here.

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class CategoryGroup(BaseModel):
    title = models.CharField(max_length=250, unique=True)
    slug = models.SlugField(null=True, blank=True)
    image = models.ImageField(upload_to='category_groups')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super(CategoryGroup, self).save(*args, **kwargs)
    def __str__(self):
        return self.title


class Category(BaseModel):
    title = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(null=True, blank=True)
    image = models.ImageField(upload_to='category')
    groups = models.ForeignKey(CategoryGroup, related_name='categories', on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super(Category, self).save(*args, **kwargs)

    def __str__(self):
        return self.title


class Brand(BaseModel):
    title = models.CharField(max_length=250, unique=True)
    slug = models.SlugField(null=True, blank=True)
    logo = models.ImageField(upload_to='brands')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super(Brand, self).save(*args, **kwargs)

    def __str__(self):
        return self.title


class Product(BaseModel):
    title = models.CharField(max_length=250, unique=True)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=14, decimal_places=2)
    discount = models.IntegerField(default=0)
    category = ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    brand = ForeignKey(Brand, related_name='products', on_delete=models.CASCADE, null=True, blank=True)

    @property
    def final_price(self):
        price = self.price * Decimal(f'{1-(self.discount / 100)}')
        return price.quantize(Decimal('1.00'))



class ProductImages(BaseModel):
    image = models.ImageField(upload_to='products')
    product = ForeignKey(Product, related_name='images', on_delete=models.CASCADE)


class AttributeValue(BaseModel):
    value = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.value

class AttributeKey(BaseModel):
    key = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.key

class ProductAttribute(BaseModel):
    key = models.ForeignKey(AttributeKey, on_delete=models.CASCADE)
    value = models.ForeignKey(AttributeValue, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='attributes')

    def __str__(self):
        return f"{self.product.title} - {self.key.key}: {self.value.value}"

class Favorite(BaseModel):
    user = models.ForeignKey(CustomUser, related_name='favorites', on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user} | {self.product}'

    class Meta:
        unique_together = ('user', 'product')


class Cart(BaseModel):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    guest_session_key = models.CharField(max_length=40, null=True, blank=True)

    @property
    def total_cart_price(self):
        return sum(item.total_item_price for item in self.items.all())

class CartItem(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f'{self.product} | {self.quantity}'

    @property
    def total_item_price(self):
        return self.product.final_price * self.quantity

    class Meta:
        unique_together = (('cart', 'product'),)



class Order(BaseModel):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    PAYMENT_STATUS = (
        ('pending', 'Pending'),
        ('successful', 'Successful'),
        ('failed', 'Failed'),
    )

    status = models.CharField(max_length=20, choices=PAYMENT_STATUS)

    @property
    def total_order_price(self):
        return sum(item.price_when_ordered * item.quantity for item in self.items.all())

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)#o'chib ketmasligi uchun
    quantity = models.PositiveIntegerField()
    price_when_ordered = models.DecimalField(max_digits=14, decimal_places=2)#productni narxi o'zgarsayam order eski narxda


class Comment(BaseModel):
    class RatingChoices(models.IntegerChoices):
        ONE = 1
        TWO = 2
        THREE = 3
        FOUR = 4
        FIVE = 5

    topic = models.CharField(max_length=100, null=True, blank=True)
    text = models.TextField()
    rating = models.IntegerField(default=RatingChoices.THREE, choices=RatingChoices.choices )
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='comments')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='comments')


