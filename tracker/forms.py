from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import Card, Document, Expense


class CardForm(forms.ModelForm):
    bank_name = forms.ChoiceField(choices=Card.BANK_CHOICES)
    card_number = forms.CharField(
        max_length=19,
        validators=[
            RegexValidator(
                regex=r"^[0-9 ]+$",
                message="Enter a valid card number using digits only.",
            )
        ],
    )
    cvv = forms.CharField(
        max_length=4,
        min_length=3,
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "123",
                "autocomplete": "off",
                "inputmode": "numeric",
            }
        ),
        help_text="Used during entry only and not stored.",
    )
    secure_note = forms.CharField(
        required=False,
        max_length=180,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Optional private note",
            }
        ),
        help_text="Visible only after you unlock card details.",
    )
    starting_balance = forms.DecimalField(
        min_value=0,
        decimal_places=2,
        max_digits=12,
        widget=forms.NumberInput(
            attrs={
                "placeholder": "12000.00",
                "step": "0.01",
                "min": "0",
            }
        ),
    )

    class Meta:
        model = Card
        fields = ["holder_name", "bank_name", "card_number", "expiry", "secure_note", "starting_balance"]
        widgets = {
            "holder_name": forms.TextInput(attrs={"placeholder": "Aisha Khan"}),
            "expiry": forms.TextInput(attrs={"placeholder": "08/29", "maxlength": "5"}),
            "secure_note": forms.TextInput(attrs={"placeholder": "Optional private note"}),
        }

    def clean_card_number(self):
        raw_value = self.cleaned_data["card_number"]
        digits = "".join(char for char in raw_value if char.isdigit())
        if len(digits) < 12 or len(digits) > 19:
            raise forms.ValidationError("Use a card number between 12 and 19 digits.")
        return digits

    def clean_expiry(self):
        expiry = self.cleaned_data["expiry"].strip()
        validator = RegexValidator(
            regex=r"^(0[1-9]|1[0-2])/[0-9]{2}$",
            message="Use MM/YY format, for example 08/29.",
        )
        validator(expiry)
        return expiry

    def clean_cvv(self):
        cvv = self.cleaned_data["cvv"].strip()
        validator = RegexValidator(
            regex=r"^[0-9]{3,4}$",
            message="Use a 3 or 4 digit CVV.",
        )
        validator(cvv)
        return cvv

    def save(self, commit=True):
        instance = super().save(commit=False)
        number = self.cleaned_data["card_number"]
        instance.full_number = number
        instance.last_four = number[-4:]
        instance.card_network = Card.network_for_number(number)
        instance.theme = Card.theme_for_bank(self.cleaned_data["bank_name"])
        if commit:
            instance.save()
        return instance


class ExpenseForm(forms.ModelForm):
    AUTO_CATEGORY = "__auto__"

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["card"].required = False
        self.fields["card"].empty_label = "Cash / Other"
        self.fields["card"].queryset = Card.objects.filter(user=user) if user else Card.objects.none()
        self.fields["card"].label_from_instance = (
            lambda card: f"{card.bank_name} - **** {card.last_four} - Balance ₹{card.available_balance:.2f}"
        )
        self.fields["category"].choices = [(self.AUTO_CATEGORY, "Auto detect")] + list(Expense.CATEGORY_CHOICES)
        if not self.is_bound:
            self.fields["date"].initial = timezone.localdate()
            self.fields["category"].initial = self.AUTO_CATEGORY
            self.fields["transaction_type"].initial = Expense.TYPE_DEBIT

    class Meta:
        model = Expense
        fields = ["title", "amount", "transaction_type", "category", "date", "card"]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "Grocery run"}),
            "amount": forms.NumberInput(attrs={"min": "0", "step": "0.01", "placeholder": "55.90"}),
            "transaction_type": forms.Select(),
            "date": forms.DateInput(attrs={"type": "date"}),
            "card": forms.Select(),
        }

    def clean_category(self):
        category = self.cleaned_data["category"]
        if category == self.AUTO_CATEGORY:
            title = self.data.get("title", "")
            if self.data.get("transaction_type") == Expense.TYPE_CREDIT:
                return Expense.CATEGORY_OTHER
            return Expense.infer_category(title)
        return category


class SignUpForm(UserCreationForm):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "yourname",
                "autocomplete": "username",
            }
        )
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={
                "placeholder": "you@example.com",
                "autocomplete": "email",
            }
        ),
    )
    password1 = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Create a password",
                "autocomplete": "new-password",
            }
        ),
    )
    password2 = forms.CharField(
        label="Confirm password",
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Repeat the same password",
                "autocomplete": "new-password",
            }
        ),
    )

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class SignInForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "yourname"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder": "Password"}))


class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = [
            "document_type",
            "theme",
            "holder_name",
            "date_of_birth",
            "aadhaar_number",
            "pan_number",
            "license_number",
            "license_valid_until",
            "vehicle_registration_number",
            "vehicle_model",
            "issuing_state",
            "notes",
        ]
        widgets = {
            "document_type": forms.Select(),
            "theme": forms.Select(),
            "holder_name": forms.TextInput(attrs={"placeholder": "Mohammed Rihan"}),
            "date_of_birth": forms.DateInput(attrs={"type": "date"}),
            "aadhaar_number": forms.TextInput(attrs={"placeholder": "1234 5678 9012", "maxlength": "14"}),
            "pan_number": forms.TextInput(attrs={"placeholder": "ABCDE1234F", "maxlength": "10"}),
            "license_number": forms.TextInput(attrs={"placeholder": "DL-0120230012345"}),
            "license_valid_until": forms.DateInput(attrs={"type": "date"}),
            "vehicle_registration_number": forms.TextInput(attrs={"placeholder": "KL 07 AB 1234"}),
            "vehicle_model": forms.TextInput(attrs={"placeholder": "Hyundai i20"}),
            "issuing_state": forms.TextInput(attrs={"placeholder": "Kerala"}),
            "notes": forms.TextInput(attrs={"placeholder": "Optional private note"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        document_type = cleaned_data.get("document_type")

        if document_type == Document.TYPE_AADHAAR:
            aadhaar_number = (cleaned_data.get("aadhaar_number") or "").replace(" ", "")
            if not aadhaar_number:
                self.add_error("aadhaar_number", "Enter the Aadhaar number.")
            elif not aadhaar_number.isdigit() or len(aadhaar_number) != 12:
                self.add_error("aadhaar_number", "Use a valid 12 digit Aadhaar number.")
            else:
                cleaned_data["aadhaar_number"] = " ".join(
                    aadhaar_number[index:index + 4] for index in range(0, 12, 4)
                )

        if document_type == Document.TYPE_PAN:
            pan_number = (cleaned_data.get("pan_number") or "").upper().strip()
            validator = RegexValidator(
                regex=r"^[A-Z]{5}[0-9]{4}[A-Z]$",
                message="Use a valid PAN format like ABCDE1234F.",
            )
            if not pan_number:
                self.add_error("pan_number", "Enter the PAN number.")
            else:
                try:
                    validator(pan_number)
                    cleaned_data["pan_number"] = pan_number
                except ValidationError as error:
                    self.add_error("pan_number", error)

        if document_type == Document.TYPE_LICENSE:
            if not cleaned_data.get("license_number"):
                self.add_error("license_number", "Enter the licence number.")
            if not cleaned_data.get("license_valid_until"):
                self.add_error("license_valid_until", "Enter the licence expiry date.")

        if document_type == Document.TYPE_RC:
            if not cleaned_data.get("vehicle_registration_number"):
                self.add_error("vehicle_registration_number", "Enter the vehicle registration number.")
            if not cleaned_data.get("vehicle_model"):
                self.add_error("vehicle_model", "Enter the vehicle model.")

        return cleaned_data
