from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse


class FoodItem(models.Model):
    CATEGORY_CHOICES = [
        ("Main Course", "Main Course"),
        ("Fast Food", "Fast Food"),
        ("Snacks", "Snacks"),
        ("Dessert", "Dessert"),
        ("Drinks", "Drinks"),
    ]

    name = models.CharField(max_length=120)
    emoji = models.CharField(max_length=10, default="🍽️")
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default="Main Course")
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    available = models.BooleanField(default=True)
    image_url = models.URLField(blank=True, help_text="Optional direct food-photo URL. Leave blank to use the emoji fallback.")
    featured = models.BooleanField(default=False)

    class Meta:
        ordering = ["category", "name"]

    def __str__(self):
        return f"{self.emoji} {self.name}"

    def get_absolute_url(self):
        return reverse("food_detail", args=[self.pk])


class Order(models.Model):
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Preparing", "Preparing"),
        ("Ready", "Ready"),
        ("Delivered", "Delivered"),
        ("Cancelled", "Cancelled"),
    ]

    PAYMENT_METHOD_CHOICES = [
        ("Cash on Delivery", "Cash on Delivery"),
        ("Card Payment", "Credit / Debit Card"),
        ("bKash", "bKash"),
        ("Nagad", "Nagad"),
        ("Rocket", "Rocket"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")
    payment_method = models.CharField(max_length=30, choices=PAYMENT_METHOD_CHOICES, default="Cash on Delivery")
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    food_item = models.ForeignKey(FoodItem, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.food_item.name} x {self.quantity}"
