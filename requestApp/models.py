from django.db import models
from customerApp.models import Customer
from stockApp.models import Stock

class StockRequest(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected')
    ]
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='requests')
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    admin_note = models.TextField(blank=True)

    def __str__(self):
        return f"{self.customer} requests {self.quantity} x {self.stock.name}"

    @property
    def total_cost(self):
        return self.quantity * self.stock.price
