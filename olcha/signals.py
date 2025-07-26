from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from .models import Cart
from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from .models import Product, Category

#user login qiganida cartlani qo'shib yuborish
@receiver(user_logged_in)
def merge_guest_cart(sender, user, request, **kwargs):
    session_key = request.session.session_key
    if not session_key:
        return

    guest_cart = Cart.objects.filter(guest_session_key=session_key).first()
    if not guest_cart:
        return

    user_cart, created = Cart.objects.get_or_create(user=user)

    for item in guest_cart.items.all():
        existing = user_cart.items.filter(product=item.product).first()
        if existing:
            existing.quantity += item.quantity
            existing.save()
        else:
            item.cart = user_cart
            item.save()

    guest_cart.delete()


@receiver([post_delete, post_save], sender=Product)
def product_list_cache_update(sender, instance=None, created=False, **kwargs):
    cache.clear()

@receiver([post_delete, post_save], sender=Category)
def category_list_cache_update(sender, instance=None, created=False, **kwargs):
    cache.clear()
