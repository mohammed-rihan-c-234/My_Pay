from django.contrib import admin

from .models import Card, Document, Expense


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ("holder_name", "last_four", "expiry", "theme", "created_at")
    search_fields = ("holder_name", "last_four")


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ("title", "amount", "category", "date", "card", "created_at")
    list_filter = ("category", "date")
    search_fields = ("title",)


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("holder_name", "document_type", "theme", "user", "created_at")
    list_filter = ("document_type", "created_at")
    search_fields = (
        "holder_name",
        "aadhaar_number",
        "pan_number",
        "license_number",
        "vehicle_registration_number",
        "user__username",
    )

# Register your models here.
