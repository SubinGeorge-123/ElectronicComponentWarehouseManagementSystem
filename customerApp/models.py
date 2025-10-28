from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    first_name = models.CharField(max_length=120)
    last_name = models.CharField(max_length=120)
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def save(self, *args, **kwargs):
        if self.user:
            self.user.email = self.email
            self.user.first_name = self.first_name
            self.user.last_name = self.last_name
            self.user.save()
        super().save(*args, **kwargs)

