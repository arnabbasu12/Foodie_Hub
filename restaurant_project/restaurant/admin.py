import csv

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.utils.html import format_html

from .models import FoodItem, Order, OrderItem

admin.site.empty_value_display = "—"


# =========================================================
# FOOD ITEM ADMIN
# =========================================================

@admin.register(FoodItem)
class FoodItemAdmin(admin.ModelAdmin):

    list_display = (
        "photo_preview",
        "name",
        "category",
        "price",
        "available",
        "featured",
    )

    list_editable = (
        "price",
        "available",
        "featured",
    )

    list_filter = (
        "category",
        "available",
        "featured",
    )

    search_fields = (
        "name",
        "description",
        "category",
    )

    list_per_page = 20

    ordering = (
        "category",
        "name",
    )

    save_on_top = True

    actions = (
        "mark_available",
        "mark_unavailable",
        "mark_featured",
        "mark_unfeatured",
    )

    readonly_fields = (
        "photo_preview_large",
    )

    fieldsets = (
        (
            "🍔 Food Information",
            {
                "fields": (
                    "name",
                    "emoji",
                    "category",
                    "description",
                    "price",
                )
            },
        ),
        (
            "🖼️ Food Photo & Visibility",
            {
                "fields": (
                    "image_url",
                    "photo_preview_large",
                    "available",
                    "featured",
                )
            },
        ),
    )

    def photo_preview(self, obj):
        """Small image preview in food list."""

        if obj.image_url:
            return format_html(
                '<img src="{}" width="60" height="60" '
                'style="object-fit:cover;border-radius:10px;" />',
                obj.image_url,
            )

        return format_html(
            '<span style="font-size:28px;">{}</span>',
            obj.emoji or "🍽️",
        )

    photo_preview.short_description = "Photo"

    def photo_preview_large(self, obj):
        """Large image preview inside edit page."""

        if obj.image_url:
            return format_html(
                '<img src="{}" width="220" height="160" '
                'style="object-fit:cover;border-radius:14px;'
                'box-shadow:0 4px 12px rgba(0,0,0,.15);" />',
                obj.image_url,
            )

        return format_html(
            '<div style="font-size:70px;">{}</div>',
            obj.emoji or "🍽️",
        )

    photo_preview_large.short_description = "Preview"

    def mark_available(self, request, queryset):
        updated = queryset.update(available=True)
        self.message_user(request, f"{updated} food item(s) marked as available.")

    mark_available.short_description = "Mark selected items as available"

    def mark_unavailable(self, request, queryset):
        updated = queryset.update(available=False)
        self.message_user(request, f"{updated} food item(s) marked as unavailable.")

    mark_unavailable.short_description = "Mark selected items as unavailable"

    def mark_featured(self, request, queryset):
        updated = queryset.update(featured=True)
        self.message_user(request, f"{updated} food item(s) marked as featured.")

    mark_featured.short_description = "Mark selected items as featured"

    def mark_unfeatured(self, request, queryset):
        updated = queryset.update(featured=False)
        self.message_user(request, f"{updated} food item(s) removed from featured.")

    mark_unfeatured.short_description = "Remove selected items from featured"


# =========================================================
# ORDER ITEM INLINE
# =========================================================

class OrderItemInline(admin.TabularInline):
    model = OrderItem

    extra = 0

    readonly_fields = (
        "food_item",
        "quantity",
        "price",
        "total",
    )

    can_delete = False


# =========================================================
# ORDER ADMIN
# =========================================================

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    # IMPORTANT:
    # status MUST be inside list_display because
    # it is also inside list_editable.
    list_display = (
        "id",
        "user",
        "status",
        "payment_method",
        "total",
        "created_at",
    )

    list_editable = (
        "status",
    )

    list_filter = (
        "status",
        "payment_method",
        "created_at",
    )

    search_fields = (
        "user__username",
        "user__email",
    )

    date_hierarchy = "created_at"

    ordering = (
        "-created_at",
    )

    list_per_page = 20

    save_on_top = True

    actions = (
        "mark_preparing",
        "mark_ready",
        "mark_delivered",
        "mark_cancelled",
        "export_orders_csv",
    )

    readonly_fields = (
        "user",
        "created_at",
        "total",
    )

    inlines = [
        OrderItemInline,
    ]

    fieldsets = (
        (
            "📦 Order Information",
            {
                "fields": (
                    "user",
                    "status",
                    "payment_method",
                    "total",
                    "created_at",
                )
            },
        ),
    )

    def mark_preparing(self, request, queryset):
        updated = queryset.update(status="Preparing")
        self.message_user(request, f"{updated} order(s) marked as Preparing.")

    mark_preparing.short_description = "Mark selected orders as Preparing"

    def mark_ready(self, request, queryset):
        updated = queryset.update(status="Ready")
        self.message_user(request, f"{updated} order(s) marked as Ready.")

    mark_ready.short_description = "Mark selected orders as Ready"

    def mark_delivered(self, request, queryset):
        updated = queryset.update(status="Delivered")
        self.message_user(request, f"{updated} order(s) marked as Delivered.")

    mark_delivered.short_description = "Mark selected orders as Delivered"

    def mark_cancelled(self, request, queryset):
        updated = queryset.update(status="Cancelled")
        self.message_user(request, f"{updated} order(s) marked as Cancelled.")

    mark_cancelled.short_description = "Mark selected orders as Cancelled"

    def export_orders_csv(self, request, queryset):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="foodiehub_orders.csv"'
        writer = csv.writer(response)
        writer.writerow(["Order ID", "Customer", "Status", "Payment Method", "Total", "Created At"])
        for order in queryset.select_related("user"):
            writer.writerow([order.id, order.user.username, order.status, order.get_payment_method_display(), order.total, order.created_at])
        return response

    export_orders_csv.short_description = "Export selected orders to CSV"


# =========================================================
# ORDER ITEM ADMIN
# =========================================================

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "order",
        "food_item",
        "quantity",
        "price",
        "total",
    )

    search_fields = (
        "food_item__name",
        "order__user__username",
    )

    list_filter = (
        "food_item",
    )

    readonly_fields = (
        "order",
        "food_item",
        "quantity",
        "price",
        "total",
    )

    list_per_page = 25


# =========================================================
# USER ADMIN
# =========================================================

# Django normally registers User automatically.
# We unregister it first so we can customize it.

try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass


@admin.register(User)
class CustomUserAdmin(UserAdmin):

    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "is_active",
        "date_joined",
    )

    list_filter = (
        "is_staff",
        "is_superuser",
        "is_active",
        "groups",
    )

    search_fields = (
        "username",
        "email",
        "first_name",
        "last_name",
    )

    ordering = (
        "-date_joined",
    )

    list_per_page = 25


# =========================================================
# ADMIN SITE SETTINGS
# =========================================================

admin.site.site_header = "🍴 FoodieHub Administration"

admin.site.site_title = "FoodieHub Admin"

admin.site.index_title = "Restaurant Management Dashboard"