# Generated manually for FoodieHub

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='payment_method',
            field=models.CharField(
                choices=[
                    ('Cash on Delivery', 'Cash on Delivery'),
                    ('Card Payment', 'Credit / Debit Card'),
                    ('bKash', 'bKash'),
                    ('Nagad', 'Nagad'),
                    ('Rocket', 'Rocket'),
                ],
                default='Cash on Delivery',
                max_length=30,
            ),
        ),
    ]
