from django.db import models

class Stock(models.Model):
    CATEGORY_CHOICES = [
        ('resistor', 'Resistor'),
        ('capacitor', 'Capacitor'),
        ('ic', 'IC'),
        ('transistor', 'Transistor'),
        ('other', 'Other')
    ]
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='other')
    quantity = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    # description = models.TextField(blank=True)
    image = models.ImageField(upload_to='stock_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
