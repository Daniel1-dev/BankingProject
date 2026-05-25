from django.db import models
from django.contrib.auth.models import User 
import uuid


# Create your models here



class Payment(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    reference = models.CharField(
        max_length=100,
        unique=True
    )

    status = models.CharField(
        max_length=20,
        default="Pending"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def save(self,*args,**kwargs):

        if not self.reference:

            self.reference = str(
                uuid.uuid4()
            )[:10]

        super().save(*args,**kwargs)



# User profile
class Profile(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    full_name = models.CharField(
        max_length=100,
        blank=True,
        default=""
    )

    profile_picture = models.ImageField(
        upload_to='profiles/',
        default='profiles',
        blank=True
    )

    bio = models.TextField(
        max_length=500,
        blank=True
    )

    weekly_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    def __str__(self):
        return self.full_name or self.user.username


class Contribution(models.Model):

    STATUS_CHOICES = [

        ('Paid','Paid'),
        ('Missed','Missed')

    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    contribution_date = models.DateField()

    week_number = models.IntegerField(null = True, blank = True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Paid'
    )

    def __str__(self):

        return f"{self.user.username} - Week {self.week_number}"

# Notes model
class Note(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    title = models.CharField(
        max_length=100
    )

    content = models.TextField()

    created = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.title



class ContributionSettings(models.Model):
    total_weeks = models.IntegerField(default=12)

    def __str__(self):
        return f"{self.total_weeks} Weeks"