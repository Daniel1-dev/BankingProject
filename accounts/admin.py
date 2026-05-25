from django.contrib import admin
from .models import Profile, Contribution


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):

    list_display = (
        'user',
        'weekly_amount'
    )


@admin.register(Contribution)
class ContributionAdmin(admin.ModelAdmin):

    list_display = (
        'user',
        'amount',
        'contribution_date',
        'week_number',
        'status'
    )

    list_filter = (
        'status',
    )

    search_fields = (
        'user__username',
    )