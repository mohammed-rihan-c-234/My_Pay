from decimal import Decimal
from decimal import InvalidOperation
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Sum
from django.shortcuts import redirect, render
from django.utils import timezone

from .forms import (
    CardForm,
    DocumentForm,
    ExpenseForm,
    ReminderForm,
    SignInForm,
    SignUpForm,
    TaskForm,
)
from .models import Card, Document, Expense, Reminder, Task

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
    today = timezone.localdate()
    report_window_end = today + timedelta(days=7)
    cards = Card.objects.filter(user=request.user)
    expenses = Expense.objects.filter(user=request.user).select_related("card")
    documents = Document.objects.filter(user=request.user)
    tasks = Task.objects.filter(user=request.user)
    reminders = Reminder.objects.filter(user=request.user)
    debit_expenses = expenses.filter(transaction_type=Expense.TYPE_DEBIT)
    credit_expenses = expenses.filter(transaction_type=Expense.TYPE_CREDIT)
    active_tab = "report"
    selected_card = None
    revealed_card = None
    reveal_error = None
    selected_document = None
    revealed_document = None
    document_reveal_error = None
    card_form = CardForm()
    expense_form = ExpenseForm(user=request.user)
    document_form = DocumentForm()
    task_form = TaskForm()
    reminder_form = ReminderForm()

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
        elif action == "add_task":
            active_tab = "tasks"
            task_form = TaskForm(request.POST)
            if task_form.is_valid():
                task = task_form.save(commit=False)
                task.user = request.user
                task.save()
                messages.success(request, "Task added to your planner.")
                return redirect("dashboard")
        elif action == "delete_task":
            active_tab = "tasks"
            task_id = request.POST.get("task_id")
            task = tasks.filter(id=task_id).first()
            if task:
                task.delete()
                messages.success(request, "Task deleted.")
                return redirect("dashboard")
            messages.error(request, "That task could not be found.")
        elif action == "add_reminder":
            active_tab = "reminders"
            reminder_form = ReminderForm(request.POST)
            if reminder_form.is_valid():
                reminder = reminder_form.save(commit=False)
                reminder.user = request.user
                reminder.save()
                messages.success(request, "Reminder saved.")
                return redirect("dashboard")
        elif action == "delete_reminder":
            active_tab = "reminders"
            reminder_id = request.POST.get("reminder_id")
            reminder = reminders.filter(id=reminder_id).first()
            if reminder:
                reminder.delete()
                messages.success(request, "Reminder deleted.")
                return redirect("dashboard")
            messages.error(request, "That reminder could not be found.")

    total_spent = debit_expenses.aggregate(total=Sum("amount"))["total"] or Decimal("0")
    total_credited = credit_expenses.aggregate(total=Sum("amount"))["total"] or Decimal("0")
    today_spent = (
        debit_expenses.filter(date=today).aggregate(total=Sum("amount"))["total"] or Decimal("0")
    )
    weekly_spent = (
        debit_expenses.filter(date__gte=today - timedelta(days=6), date__lte=today).aggregate(total=Sum("amount"))["total"]
        or Decimal("0")
    )
    category_totals = (
        debit_expenses.values("category")
        .annotate(total=Sum("amount"))
        .order_by("-total", "category")
    )
    tasks_due_today = tasks.filter(due_date=today)
    overdue_tasks = tasks.filter(due_date__lt=today)
    upcoming_tasks = tasks.filter(due_date__gt=today, due_date__lte=report_window_end)
    reminders_today = reminders.filter(remind_on=today)
    upcoming_reminders = reminders.filter(remind_on__gt=today, remind_on__lte=report_window_end)
    expiring_documents = documents.filter(
        document_type=Document.TYPE_LICENSE,
        license_valid_until__isnull=False,
        license_valid_until__lte=report_window_end,
    ).order_by("license_valid_until")
    report_cards = [
        {
            "label": "Today's spend",
            "value": f"₹{today_spent:.2f}",
            "meta": f"Last 7 days ₹{weekly_spent:.2f}",
            "theme": "sunrise",
        },
        {
            "label": "Tasks due",
            "value": tasks_due_today.count() + overdue_tasks.count(),
            "meta": (
                f"{overdue_tasks.count()} overdue, {tasks_due_today.count()} due today"
                if tasks_due_today.exists() or overdue_tasks.exists()
                else "Nothing urgent today"
            ),
            "theme": "berry",
        },
        {
            "label": "Reminders today",
            "value": reminders_today.count(),
            "meta": (
                f"{upcoming_reminders.count()} more coming this week"
                if reminders_today.exists() or upcoming_reminders.exists()
                else "No reminders scheduled"
            ),
            "theme": "ocean",
        },
        {
            "label": "Expiring docs",
            "value": expiring_documents.count(),
            "meta": "Driving licences expiring within 7 days",
            "theme": "gold",
        },
    ]

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
        "saved_tasks_count": tasks.count(),
        "saved_reminders_count": reminders.count(),
        "active_tab": active_tab,
        "selected_card": selected_card,
        "revealed_card": revealed_card,
        "reveal_error": reveal_error,
        "documents": documents,
        "document_form": document_form,
        "selected_document": selected_document,
        "revealed_document": revealed_document,
        "document_reveal_error": document_reveal_error,
        "tasks": tasks,
        "task_form": task_form,
        "reminders": reminders,
        "reminder_form": reminder_form,
        "today": today,
        "tasks_due_today": tasks_due_today,
        "overdue_tasks": overdue_tasks,
        "upcoming_tasks": upcoming_tasks,
        "reminders_today": reminders_today,
        "upcoming_reminders": upcoming_reminders,
        "expiring_documents": expiring_documents,
        "report_cards": report_cards,
        "today_spent": today_spent,
    }
    return render(request, "tracker/dashboard.html", context)

# Create your views here.
