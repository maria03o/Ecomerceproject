from django import template
from catalog.models import Order

register = template.Library()

@register.filter
def cart_total_items(user):
    if user.is_authenticated:
        order = Order.objects.filter(user=user, ordered=False).first()
        if order:
            return order.items.count()
    return 0
