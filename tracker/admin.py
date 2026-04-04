from django.contrib import admin

from .models import Card, Expense


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ("holder_name", "last_four", "expiry", "theme", "created_at")
    search_fields = ("holder_name", "last_four")


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ("title", "amount", "category", "date", "card", "created_at")
    list_filter = ("category", "date")
    search_fields = ("title",)

# Register your models here.
