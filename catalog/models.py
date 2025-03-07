from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

CATEGORY_CHOICES = (
    ('S', 'Shirt'),
    ('SW', 'Sport Wear'),
    ('OW', 'Outwear'),
)

LABEL_CHOICES = (
    ('S', 'Secondary'),
    ('P', 'Primary'),
    ('D', 'Danger'),
)

class Item(models.Model):
    title = models.CharField(max_length=100)
    price = models.IntegerField()
    discount_price = models.IntegerField(blank=True, null=True)
    slug = models.SlugField(unique=True)
    status = models.CharField(max_length=200)
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=2)
    label = models.CharField(choices=LABEL_CHOICES, max_length=1)
    description = models.TextField()
    image = models.ImageField(default='default.jpg', upload_to='static/images')

    def __str__(self):
        return self.title

    def get_add_to_cart_url(self):
        return reverse('add_to_cart', kwargs={'slug': self.slug})

    def get_remove_from_cart_url(self):
        return reverse('remove_from_cart', kwargs={'slug': self.slug})


class OrderItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.item.title}"

    def get_total_item_price(self):
        if self.item.discount_price:
            return self.item.discount_price * self.quantity
        return self.item.price * self.quantity

    def get_increase_quantity_url(self):
        return reverse("add_to_cart", kwargs={"slug": self.item.slug})

    def get_decrease_quantity_url(self):
        return reverse("remove_single_item", kwargs={"slug": self.item.slug})

    def get_remove_from_cart_url(self):
        return reverse("remove_from_cart", kwargs={"slug": self.item.slug})


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    items = models.ManyToManyField(OrderItem, related_name="orders")
    ordered = models.BooleanField(default=False)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"

    def get_total_price(self):
        return sum(item.get_total_item_price() for item in self.items.all())
 

from django.conf import settings
from django.http import JsonResponse
import stripe 

stripe.api_key = settings.STRIPE_SECRET_KEY  # Ensure this key is set in settings.py

def create_checkout_session(request):
    if request.method == "POST":
        order = Order.objects.filter(user=request.user, ordered=False).first()
        if not order:
            return JsonResponse({"error": "No active order found"}, status=400)

        line_items = []
        for item in order.items.all():
            line_items.append({
                "price_data": {
                    "currency": "usd",
                    "product_data": {"name": item.item.title},
                    "unit_amount": int(item.item.price * 100),  # Stripe uses cents
                },
                "quantity": item.quantity,
            })

        try:
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=line_items,
                mode="payment",
                success_url="http://127.0.0.1:8000/success/",
                cancel_url="http://127.0.0.1:8000/cancel/",
            )
            return JsonResponse({"id": session.id})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

