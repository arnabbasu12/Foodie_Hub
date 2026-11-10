from decimal import Decimal
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import LoginForm, RegisterForm
from .models import FoodItem, Order, OrderItem


def home(request):
    featured = FoodItem.objects.filter(available=True, featured=True)[:8]
    if not featured.exists():
        featured = FoodItem.objects.filter(available=True)[:8]
    return render(request, "home.html", {"featured": featured})


def menu(request):
    foods = FoodItem.objects.filter(available=True)
    q = request.GET.get("q", "").strip()
    category = request.GET.get("category", "").strip()
    if q:
        foods = foods.filter(name__icontains=q)
    if category:
        foods = foods.filter(category=category)
    categories = sorted(set(FoodItem.objects.filter(available=True).values_list("category", flat=True)))
    return render(request, "menu.html", {
        "foods": foods,
        "categories": categories,
        "query": q,
        "selected_category": category,
    })


def food_detail(request, pk):
    food = get_object_or_404(FoodItem, pk=pk, available=True)
    return render(request, "food_detail.html", {"food": food})


def _get_cart(request):
    return request.session.get("cart", {})


def cart(request):
    cart_data = _get_cart(request)
    items = []
    grand_total = Decimal("0.00")

    for pk, qty in cart_data.items():
        try:
            food = FoodItem.objects.get(pk=pk, available=True)
        except FoodItem.DoesNotExist:
            continue
        qty = int(qty)
        line_total = food.price * qty
        grand_total += line_total
        items.append({"food": food, "quantity": qty, "total": line_total})

    return render(request, "cart.html", {"items": items, "grand_total": grand_total})


@login_required
def add_to_cart(request, pk):
    food = get_object_or_404(FoodItem, pk=pk, available=True)
    cart_data = _get_cart(request)
    key = str(food.pk)
    cart_data[key] = int(cart_data.get(key, 0)) + 1
    request.session["cart"] = cart_data
    request.session.modified = True
    messages.success(request, f"{food.name} added to your cart.")
    return redirect(request.POST.get("next") or request.GET.get("next") or "menu")


@login_required
def remove_from_cart(request, pk):
    cart_data = _get_cart(request)
    key = str(pk)
    if key in cart_data:
        del cart_data[key]
        request.session["cart"] = cart_data
        request.session.modified = True
        messages.info(request, "Item removed from cart.")
    return redirect("cart")


@login_required
def clear_cart(request):
    request.session["cart"] = {}
    request.session.modified = True
    messages.info(request, "Your cart has been cleared.")
    return redirect("cart")


@login_required
def checkout(request):
    cart_data = _get_cart(request)
    items = []
    grand_total = Decimal("0.00")

    for pk, qty in cart_data.items():
        try:
            food = FoodItem.objects.get(pk=pk, available=True)
        except FoodItem.DoesNotExist:
            continue
        qty = int(qty)
        line_total = food.price * qty
        grand_total += line_total
        items.append({"food": food, "quantity": qty, "total": line_total})

    if not items:
        messages.warning(request, "Your cart is empty.")
        return redirect("menu")

    if request.method == "POST":
        payment_method = request.POST.get("payment_method")
        valid_methods = dict(Order.PAYMENT_METHOD_CHOICES)
        if payment_method not in valid_methods:
            payment_method = "Cash on Delivery"

        order = Order.objects.create(user=request.user, total=grand_total, payment_method=payment_method)
        for item in items:
            OrderItem.objects.create(
                order=order,
                food_item=item["food"],
                quantity=item["quantity"],
                price=item["food"].price,
                total=item["total"],
            )
        request.session["cart"] = {}
        request.session.modified = True
        return redirect("order_success", pk=order.pk)

    return render(request, "checkout.html", {
        "items": items,
        "grand_total": grand_total,
        "payment_methods": Order.PAYMENT_METHOD_CHOICES,
    })


@login_required
def order_success(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    return render(request, "order_success.html", {"order": order})


@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).prefetch_related("items__food_item")
    return render(request, "my_orders.html", {"orders": orders})


def user_login(request):
    if request.user.is_authenticated:
        return redirect("home")

    form = LoginForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = authenticate(
            request,
            username=form.cleaned_data["username"],
            password=form.cleaned_data["password"],
        )
        if user:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect(request.GET.get("next") or "home")
        form.add_error(None, "Invalid username or password.")

    return render(request, "auth/login.html", {"form": form})


def register(request):
    if request.user.is_authenticated:
        return redirect("home")

    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = User.objects.create_user(
            username=form.cleaned_data["username"],
            email=form.cleaned_data["email"],
            password=form.cleaned_data["password"],
        )
        login(request, user)
        messages.success(request, "Account created successfully!")
        return redirect("home")

    return render(request, "auth/register.html", {"form": form})


def user_logout(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("home")


@staff_member_required
def dashboard(request):
    orders = Order.objects.select_related("user").prefetch_related("items__food_item")
    pending_count = orders.filter(status="Pending").count()
    preparing_count = orders.filter(status="Preparing").count()
    delivered_count = orders.filter(status="Delivered").count()
    total_revenue = sum((order.total for order in orders if order.status != "Cancelled"), Decimal("0.00"))
    return render(request, "dashboard.html", {
        "orders": orders,
        "pending_count": pending_count,
        "preparing_count": preparing_count,
        "delivered_count": delivered_count,
        "total_revenue": total_revenue,
        "status_choices": Order.STATUS_CHOICES,
    })


@staff_member_required
def update_order_status(request, pk):
    if request.method == "POST":
        order = get_object_or_404(Order, pk=pk)
        status = request.POST.get("status")
        valid = dict(Order.STATUS_CHOICES)
        if status in valid:
            order.status = status
            order.save(update_fields=["status"])
            messages.success(request, f"Order #{order.pk} status updated to {status}.")
    return redirect("dashboard")
