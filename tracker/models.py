from decimal import Decimal
import os
from datetime import timedelta

from django.contrib.auth.models import User
from django.db import models
from django.db.models import Sum
from django.utils import timezone


def document_upload_to(instance, filename):
    extension = os.path.splitext(filename)[1].lower()
    safe_name = f"{instance.document_type}_{instance.user_id}{extension}"
    return f"documents/user_{instance.user_id}/{safe_name}"


class Card(models.Model):
    THEME_DEFAULT = "default"
    THEME_FEDERAL = "federal"
    THEME_KOTAK = "kotak"
    THEME_SBI = "sbi"
    THEME_HDFC = "hdfc"
    THEME_ICICI = "icici"

    THEME_CHOICES = [
        (THEME_DEFAULT, "Default"),
        (THEME_FEDERAL, "Federal"),
        (THEME_KOTAK, "Kotak"),
        (THEME_SBI, "SBI"),
        (THEME_HDFC, "HDFC"),
        (THEME_ICICI, "ICICI"),
    ]
    BANK_CHOICES = [
        ("Federal Bank", "Federal Bank"),
        ("Kotak Mahindra Bank", "Kotak Mahindra Bank"),
        ("State Bank of India", "State Bank of India"),
        ("HDFC Bank", "HDFC Bank"),
        ("ICICI Bank", "ICICI Bank"),
        ("Axis Bank", "Axis Bank"),
        ("Punjab National Bank", "Punjab National Bank"),
        ("Bank of Baroda", "Bank of Baroda"),
        ("Canara Bank", "Canara Bank"),
        ("IndusInd Bank", "IndusInd Bank"),
        ("IDFC FIRST Bank", "IDFC FIRST Bank"),
        ("Yes Bank", "Yes Bank"),
        ("South Indian Bank", "South Indian Bank"),
        ("Union Bank of India", "Union Bank of India"),
        ("IDBI Bank", "IDBI Bank"),
        ("Bandhan Bank", "Bandhan Bank"),
        ("AU Small Finance Bank", "AU Small Finance Bank"),
        ("Standard Chartered", "Standard Chartered"),
        ("HSBC", "HSBC"),
    ]
    BANK_THEME_KEYWORDS = {
        THEME_FEDERAL: ["federal bank", "south indian bank"],
        THEME_KOTAK: ["kotak", "axis bank", "indusind bank", "yes bank"],
        THEME_SBI: [
            "state bank of india",
            "sbi",
            "punjab national bank",
            "pnb",
            "bank of baroda",
            "bob",
            "canara bank",
            "union bank",
            "idbi bank",
        ],
        THEME_HDFC: ["hdfc bank", "idfc first bank", "bandhan bank", "au small finance bank"],
        THEME_ICICI: ["icici bank", "hsbc", "standard chartered"],
    }

    holder_name = models.CharField(max_length=120)
    bank_name = models.CharField(max_length=120, default="My Bank")
    secure_note = models.CharField(max_length=180, blank=True, default="")
    starting_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    full_number = models.CharField(max_length=19, blank=True, default="")
    last_four = models.CharField(max_length=4)
    expiry = models.CharField(max_length=5)
    card_network = models.CharField(max_length=30, default="Card")
    theme = models.CharField(max_length=20, choices=THEME_CHOICES, default=THEME_DEFAULT)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cards")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    @classmethod
    def theme_for_bank(cls, bank_name):
        clean_name = (bank_name or "").strip().lower()
        if not clean_name:
            return cls.THEME_DEFAULT

        for theme, keywords in cls.BANK_THEME_KEYWORDS.items():
            if any(keyword in clean_name for keyword in keywords):
                return theme

        return cls.THEME_DEFAULT

    @classmethod
    def network_for_number(cls, card_number):
        digits = "".join(char for char in (card_number or "") if char.isdigit())
        if not digits:
            return "Card"

        if digits.startswith("4"):
            return "Visa"

        first_two = int(digits[:2]) if len(digits) >= 2 else 0
        first_three = int(digits[:3]) if len(digits) >= 3 else 0
        first_four = int(digits[:4]) if len(digits) >= 4 else 0
        first_six = int(digits[:6]) if len(digits) >= 6 else 0

        if 51 <= first_two <= 55 or 2221 <= first_four <= 2720 or 222100 <= first_six <= 272099:
            return "Mastercard"
        if digits.startswith(("34", "37")):
            return "American Express"
        if digits.startswith(("60", "65", "81", "82", "508")):
            return "RuPay"
        if digits.startswith("6011") or digits.startswith("65") or 644 <= first_three <= 649:
            return "Discover"
        return "Card"

    @property
    def resolved_theme(self):
        return self.theme_for_bank(self.bank_name)

    @property
    def formatted_full_number(self):
        digits = "".join(char for char in (self.full_number or "") if char.isdigit())
        if not digits:
            return "Not available"
        return " ".join(digits[index:index + 4] for index in range(0, len(digits), 4))

    @property
    def available_balance(self):
        return self.starting_balance + self.total_credits - self.total_debits

    @property
    def total_debits(self):
        if not self.pk:
            return Decimal("0")
        return self.expenses.filter(transaction_type=Expense.TYPE_DEBIT).aggregate(
            total=Sum("amount")
        )["total"] or Decimal("0")

    @property
    def total_credits(self):
        if not self.pk:
            return Decimal("0")
        return self.expenses.filter(transaction_type=Expense.TYPE_CREDIT).aggregate(
            total=Sum("amount")
        )["total"] or Decimal("0")

    @property
    def transaction_offset(self):
        return self.total_credits - self.total_debits

    def __str__(self):
        return f"{self.bank_name} - **** {self.last_four}"


class Expense(models.Model):
    TYPE_DEBIT = "debit"
    TYPE_CREDIT = "credit"

    TRANSACTION_TYPE_CHOICES = [
        (TYPE_DEBIT, "Spend"),
        (TYPE_CREDIT, "Credit"),
    ]

    CATEGORY_FOOD = "Food"
    CATEGORY_TRANSPORT = "Transport"
    CATEGORY_BILLS = "Bills"
    CATEGORY_SHOPPING = "Shopping"
    CATEGORY_HEALTH = "Health"
    CATEGORY_ENTERTAINMENT = "Entertainment"
    CATEGORY_OTHER = "Other"

    CATEGORY_CHOICES = [
        (CATEGORY_FOOD, "Food"),
        (CATEGORY_TRANSPORT, "Transport"),
        (CATEGORY_BILLS, "Bills"),
        (CATEGORY_SHOPPING, "Shopping"),
        (CATEGORY_HEALTH, "Health"),
        (CATEGORY_ENTERTAINMENT, "Entertainment"),
        (CATEGORY_OTHER, "Other"),
    ]

    title = models.CharField(max_length=140)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE_CHOICES, default=TYPE_DEBIT)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default=CATEGORY_OTHER)
    date = models.DateField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="expenses")
    card = models.ForeignKey(
        Card,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="expenses",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-created_at"]

    def __str__(self):
        return f"{self.title} - {self.amount}"

    @property
    def signed_amount(self):
        if self.transaction_type == self.TYPE_CREDIT:
            return f"+{self.amount}"
        return f"-{self.amount}"

    @property
    def destination_label(self):
        if self.card:
            return self.card.bank_name
        return "Cash"

    @classmethod
    def infer_category(cls, title):
        title_text = (title or "").strip().lower()
        keyword_map = {
            cls.CATEGORY_FOOD: [
                "grocery",
                "groceries",
                "restaurant",
                "cafe",
                "coffee",
                "food",
                "swiggy",
                "zomato",
                "pizza",
                "burger",
            ],
            cls.CATEGORY_TRANSPORT: [
                "uber",
                "ola",
                "metro",
                "petrol",
                "fuel",
                "bus",
                "taxi",
                "train",
                "parking",
            ],
            cls.CATEGORY_BILLS: [
                "rent",
                "electricity",
                "water",
                "internet",
                "wifi",
                "phone",
                "recharge",
                "bill",
                "emi",
            ],
            cls.CATEGORY_SHOPPING: [
                "amazon",
                "flipkart",
                "myntra",
                "ajio",
                "shopping",
                "clothes",
                "shoes",
            ],
            cls.CATEGORY_HEALTH: [
                "hospital",
                "doctor",
                "pharmacy",
                "medicine",
                "clinic",
                "health",
                "apollo",
            ],
            cls.CATEGORY_ENTERTAINMENT: [
                "netflix",
                "prime",
                "movie",
                "cinema",
                "spotify",
                "game",
                "entertainment",
            ],
        }

        for category, keywords in keyword_map.items():
            if any(keyword in title_text for keyword in keywords):
                return category
        return cls.CATEGORY_OTHER


class Document(models.Model):
    TYPE_AADHAAR = "aadhaar"
    TYPE_LICENSE = "license"
    TYPE_PAN = "pan"
    TYPE_RC = "rc"
    THEME_SAFFRON = "saffron"
    THEME_MIDNIGHT = "midnight"
    THEME_EMERALD = "emerald"
    THEME_AURORA = "aurora"
    THEME_SUNSET = "sunset"
    THEME_ROYAL = "royal"

    TYPE_CHOICES = [
        (TYPE_AADHAAR, "Aadhaar Card"),
        (TYPE_LICENSE, "Driving Licence"),
        (TYPE_PAN, "PAN Card"),
        (TYPE_RC, "Vehicle RC"),
    ]
    THEME_CHOICES = [
        (THEME_SAFFRON, "Saffron Glow"),
        (THEME_MIDNIGHT, "Midnight Glass"),
        (THEME_EMERALD, "Emerald Leaf"),
        (THEME_AURORA, "Aurora Pulse"),
        (THEME_SUNSET, "Sunset Fade"),
        (THEME_ROYAL, "Royal Indigo"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="documents")
    document_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    theme = models.CharField(max_length=20, choices=THEME_CHOICES, default=THEME_AURORA)
    holder_name = models.CharField(max_length=120)
    date_of_birth = models.DateField(null=True, blank=True)
    aadhaar_number = models.CharField(max_length=14, blank=True)
    pan_number = models.CharField(max_length=10, blank=True)
    license_number = models.CharField(max_length=25, blank=True)
    license_valid_until = models.DateField(null=True, blank=True)
    vehicle_registration_number = models.CharField(max_length=20, blank=True)
    vehicle_model = models.CharField(max_length=80, blank=True)
    issuing_state = models.CharField(max_length=60, blank=True)
    notes = models.CharField(max_length=180, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["document_type", "-created_at"]

    def __str__(self):
        return f"{self.get_document_type_display()} - {self.holder_name}"

    @property
    def primary_identifier(self):
        mapping = {
            self.TYPE_AADHAAR: self.aadhaar_number,
            self.TYPE_PAN: self.pan_number,
            self.TYPE_LICENSE: self.license_number,
            self.TYPE_RC: self.vehicle_registration_number,
        }
        return mapping.get(self.document_type, "")

    @property
    def masked_identifier(self):
        identifier = (self.primary_identifier or "").replace(" ", "")
        if len(identifier) <= 4:
            return identifier
        return f"{'*' * max(len(identifier) - 4, 0)}{identifier[-4:]}"

    @property
    def days_until_expiry(self):
        if not self.license_valid_until:
            return None
        return (self.license_valid_until - timezone.localdate()).days


class ThemeMixin(models.Model):
    THEME_SUNRISE = "sunrise"
    THEME_OCEAN = "ocean"
    THEME_FOREST = "forest"
    THEME_BERRY = "berry"
    THEME_GRAPHITE = "graphite"
    THEME_GOLD = "gold"

    THEME_CHOICES = [
        (THEME_SUNRISE, "Sunrise"),
        (THEME_OCEAN, "Ocean"),
        (THEME_FOREST, "Forest"),
        (THEME_BERRY, "Berry"),
        (THEME_GRAPHITE, "Graphite"),
        (THEME_GOLD, "Gold"),
    ]

    theme = models.CharField(max_length=20, choices=THEME_CHOICES, default=THEME_OCEAN)

    class Meta:
        abstract = True


class Task(ThemeMixin):
    PRIORITY_LOW = "low"
    PRIORITY_MEDIUM = "medium"
    PRIORITY_HIGH = "high"

    PRIORITY_CHOICES = [
        (PRIORITY_LOW, "Low"),
        (PRIORITY_MEDIUM, "Medium"),
        (PRIORITY_HIGH, "High"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tasks")
    title = models.CharField(max_length=140)
    notes = models.CharField(max_length=220, blank=True)
    due_date = models.DateField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default=PRIORITY_MEDIUM)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["due_date", "-created_at"]

    def __str__(self):
        return self.title

    @property
    def due_state(self):
        today = timezone.localdate()
        if self.due_date < today:
            return "Overdue"
        if self.due_date == today:
            return "Due today"
        return "Upcoming"

    @property
    def due_in_days(self):
        return (self.due_date - timezone.localdate()).days


class Reminder(ThemeMixin):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reminders")
    title = models.CharField(max_length=140)
    note = models.CharField(max_length=220, blank=True)
    remind_on = models.DateField()
    remind_at = models.TimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["remind_on", "remind_at", "-created_at"]

    def __str__(self):
        return self.title

    @property
    def status_label(self):
        today = timezone.localdate()
        if self.remind_on < today:
            return "Missed"
        if self.remind_on == today:
            return "Today"
        if self.remind_on <= today + timedelta(days=1):
            return "Tomorrow"
        return "Upcoming"

    @property
    def days_until(self):
        return (self.remind_on - timezone.localdate()).days

# Create your models here.
