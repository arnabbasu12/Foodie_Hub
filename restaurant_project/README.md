# FoodieHub

A Django-based food ordering website with a customer-facing menu/cart/checkout flow,
order history, a staff dashboard, and a customized Django Admin panel.

## What was fixed in this update

- **Server crash on `/admin/...` list pages fixed**: `AttributeError: 'super' object
  has no attribute 'dicts'`. This was **not a bug in the project code** — it's a
  known incompatibility between **Django 4.2** and **Python 3.14** (Django only
  added official Python 3.14 support starting with Django 5.2). Since your
  environment is running Python 3.14.6, the fix is to upgrade Django itself.
  `requirements.txt` now pins `Django>=5.2,<6.0`. **After pulling this update,
  run `pip install --upgrade -r requirements.txt` inside your existing virtual
  environment** (no other code changes were needed for this — the project was
  already written using standard, forward-compatible Django APIs).
- **New: multiple payment methods**. Checkout now lets the customer choose
  between Cash on Delivery, Card Payment, bKash, Nagad, or Rocket. The chosen
  method is stored on the order and shown on the confirmation page, "My
  Orders", the staff dashboard, and the Django Admin (with a filter and CSV
  export). A new migration (`0002_order_payment_method`) adds this field — run
  `python manage.py migrate` to apply it.
- **Crash bug fixed**: clicking "Add to Cart" from a food's detail page threw a
  `NoReverseMatch` server error. The redirect now resolves correctly.
- **Food photos**: the detail page and the cart page were only showing an emoji
  instead of the actual food photo (the CSS for it existed but was never wired up).
  Both now show a properly-sized photo next to the food name, with a graceful
  emoji fallback when an item has no photo URL.
- **Logout**: added a clearly visible, high-contrast "Logout" button in the navbar
  (in addition to the account dropdown), so it's no longer easy to miss.
- **Buttons**: improved color contrast, hover states, and focus outlines across
  the site so every button is clearly readable and clickable.
- **Missing styles**: several page sections (order confirmation, login/register,
  empty cart, dashboard stat cards) referenced CSS classes that were never
  defined, so they rendered unstyled. All of these now have proper styling.
- **Admin panel**: added bulk actions (mark items available/unavailable,
  mark featured, bulk order-status updates) and a CSV export for orders.

## Setup (fresh install)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py seed_data
python manage.py createsuperuser
python manage.py runserver
```

## Updating an existing environment

If you already have a virtual environment from before (this is what fixes the
admin crash), run:

```powershell
pip install --upgrade -r requirements.txt
python manage.py migrate
```

Website: http://127.0.0.1:8000/
Admin: http://127.0.0.1:8000/admin/

The project already ships with a seeded `db.sqlite3` containing 35 sample menu
items with photos. Re-running `seed_data` is safe — it updates existing items
rather than duplicating them. You'll still need `createsuperuser` to get into
the admin panel and staff dashboard.
