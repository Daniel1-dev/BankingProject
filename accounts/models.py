from django.db import models
from django.contrib.auth.models import User 
import uuid


# Create your models here




class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100, blank=True, default="")
    profile_picture = models.ImageField(upload_to='profiles/', default='profiles', blank=True)
    bio = models.TextField(max_length=500, blank=True)
    phone_number = models.CharField(max_length=15, blank=True, default="")
    address = models.TextField(blank=True, default="")
    gender = models.CharField(max_length=10, blank=True, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    is_suspended = models.BooleanField(default=False)
    suspension_reason = models.TextField(blank=True, default="")
    suspended_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.full_name or self.user.username

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('Deposit', 'Deposit'),
        ('Withdrawal', 'Withdrawal'),
        ('Transfer', 'Transfer'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    description = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    reference = models.CharField(max_length=100, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = str(uuid.uuid4()).replace('-', '')[:15].upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.transaction_type} - {self.amount}"

class Transfer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    bank_name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=20)
    account_name = models.CharField(max_length=100)
    reference = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, default='Pending')
    timestamp = models.DateTimeField(auto_now_add=True)
