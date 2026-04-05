from decimal import Decimal
from decimal import InvalidOperation

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Sum
from django.shortcuts import redirect, render

from .forms import CardForm, DocumentForm, ExpenseForm, SignInForm, SignUpForm
from .models import Card, Document, Expense

EXPENSE_CATEGORY_COLORS = {
    Expense.CATEGORY_FOOD: "#f97316",
    Expense.CATEGORY_TRANSPORT: "#3b82f6",
    Expense.CATEGORY_BILLS: "#8b5cf6",
    Expense.CATEGORY_SHOPPING: "#ec4899",
    Expense.CATEGORY_HEALTH: "#10b981",
    Expense.CATEGORY_ENTERTAINMENT: "#f59e0b",
    Expense.CATEGORY_OTHER: "#6b7280",
}


def health_check(request):
    return JsonResponse({"status": "ok"})


def landing(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    return redirect("login")


def signup_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Your account is ready.")
            return redirect("dashboard")
    else:
        form = SignUpForm()

    return render(
        request,
        "tracker/auth.html",
        {
            "form": form,
            "title": "Create account",
            "heading": "Create your account",
            "submit_label": "Sign up",
            "switch_text": "Already have an account?",
            "switch_url": "login",
            "switch_label": "Sign in",
        },
    )


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        form = SignInForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            messages.success(request, "Welcome back.")
            return redirect("dashboard")
    else:
        form = SignInForm()

    return render(
        request,
        "tracker/auth.html",
        {
            "form": form,
            "title": "Sign in",
            "heading": "Sign in to ExpenseFlow",
            "submit_label": "Sign in",
            "switch_text": "Need an account?",
            "switch_url": "signup",
            "switch_label": "Create one",
        },
    )


@login_required
def dashboard(request):
    cards = Card.objects.filter(user=request.user)
    expenses = Expense.objects.filter(user=request.user).select_related("card")
    documents = Document.objects.filter(user=request.user)
    debit_expenses = expenses.filter(transaction_type=Expense.TYPE_DEBIT)
    credit_expenses = expenses.filter(transaction_type=Expense.TYPE_CREDIT)
    active_tab = "wallet"
    selected_card = None
    revealed_card = None
    reveal_error = None
    selected_document = None
    revealed_document = None
    document_reveal_error = None
    card_form = CardForm()
    expense_form = ExpenseForm(user=request.user)
    document_form = DocumentForm()

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "add_card":
            active_tab = "wallet"
            card_form = CardForm(request.POST)
            if card_form.is_valid():
                card = card_form.save(commit=False)
                card.user = request.user
                card.save()
                messages.success(request, "Card saved to the wallet.")
                return redirect("dashboard")
        elif action == "add_expense":
            active_tab = "expenses"
            expense_form = ExpenseForm(request.POST, user=request.user)
            if expense_form.is_valid():
                expense = expense_form.save(commit=False)
                expense.user = request.user
                expense.save()
                if expense.card:
                    messages.success(
                        request,
                        f"Transaction saved. {expense.card.bank_name} balance is now ₹{expense.card.available_balance:.2f}.",
                    )
                else:
                    messages.success(request, "Transaction saved to the tracker.")
                return redirect("dashboard")
        elif action == "clear_expenses":
            expenses.delete()
            messages.success(request, "All expenses were cleared.")
            return redirect("dashboard")
        elif action == "delete_card":
            active_tab = "wallet"
            card_id = request.POST.get("card_id")
            card_to_delete = cards.filter(id=card_id).first()
            if card_to_delete:
                card_to_delete.delete()
                messages.success(request, "Card removed from your wallet.")
                return redirect("dashboard")
            messages.error(request, "That card could not be found.")
        elif action == "reveal_card":
            active_tab = "wallet"
            card_id = request.POST.get("card_id")
            password = request.POST.get("account_password", "")
            selected_card = cards.filter(id=card_id).first()
            if not selected_card:
                reveal_error = "That card could not be found."
            elif not request.user.check_password(password):
                reveal_error = "The password you entered is incorrect."
            else:
                revealed_card = selected_card
        elif action == "update_balance":
            active_tab = "wallet"
            card_id = request.POST.get("card_id")
            selected_card = cards.filter(id=card_id).first()
            if not selected_card:
                reveal_error = "That card could not be found."
            else:
                try:
                    desired_balance = Decimal(request.POST.get("new_balance", "0"))
                    if desired_balance < 0:
                        raise InvalidOperation
                    selected_card.starting_balance = desired_balance - selected_card.transaction_offset
                    selected_card.save(update_fields=["starting_balance"])
                    revealed_card = selected_card
                    messages.success(request, "Balance updated.")
                except (InvalidOperation, TypeError):
                    reveal_error = "Enter a valid balance amount."
                    revealed_card = selected_card
        elif action == "add_document":
            active_tab = "documents"
            document_form = DocumentForm(request.POST)
            if document_form.is_valid():
                document = document_form.save(commit=False)
                document.user = request.user
                document.save()
                messages.success(request, "Document card saved securely.")
                return redirect("dashboard")
        elif action == "reveal_document":
            active_tab = "documents"
            document_id = request.POST.get("document_id")
            password = request.POST.get("account_password", "")
            selected_document = documents.filter(id=document_id).first()
            if not selected_document:
                document_reveal_error = "That document could not be found."
            elif not request.user.check_password(password):
                document_reveal_error = "The password you entered is incorrect."
            else:
                revealed_document = selected_document
        elif action == "delete_document":
            active_tab = "documents"
            document_id = request.POST.get("document_id")
            document = documents.filter(id=document_id).first()
            if document:
                document.delete()
                messages.success(request, "Document removed.")
                return redirect("dashboard")
            messages.error(request, "That document could not be found.")

    total_spent = debit_expenses.aggregate(total=Sum("amount"))["total"] or Decimal("0")
    total_credited = credit_expenses.aggregate(total=Sum("amount"))["total"] or Decimal("0")
    category_totals = (
        debit_expenses.values("category")
        .annotate(total=Sum("amount"))
        .order_by("-total", "category")
    )

    top_category = category_totals[0] if category_totals else None
    summary_cards = []
    for item in category_totals:
        total = item["total"] or Decimal("0")
        percent = round((total / total_spent) * 100) if total_spent else 0
        summary_cards.append(
            {
                "category": item["category"],
                "total": total,
                "percent": percent,
                "color": EXPENSE_CATEGORY_COLORS.get(item["category"], EXPENSE_CATEGORY_COLORS[Expense.CATEGORY_OTHER]),
            }
        )

    context = {
        "card_form": card_form,
        "expense_form": expense_form,
        "cards": cards,
        "expenses": expenses,
        "total_spent": total_spent,
        "total_credited": total_credited,
        "summary_cards": summary_cards,
        "top_category": top_category,
        "saved_cards_count": cards.count(),
        "saved_documents_count": documents.count(),
        "active_tab": active_tab,
        "selected_card": selected_card,
        "revealed_card": revealed_card,
        "reveal_error": reveal_error,
        "documents": documents,
        "document_form": document_form,
        "selected_document": selected_document,
        "revealed_document": revealed_document,
        "document_reveal_error": document_reveal_error,
    }
    return render(request, "tracker/dashboard.html", context)

# Create your views here.
