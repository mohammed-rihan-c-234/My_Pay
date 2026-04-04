# ExpenseFlow

ExpenseFlow is a Django-based personal finance app with:

- wallet-style saved cards
- expense and credit tracking
- automatic category detection from expense titles
- per-card balance tracking
- protected card detail reveal using your account password

## Features

- User accounts with login and signup
- Apple Pay-inspired card wallet UI
- Bank-based card themes
- Card network detection such as Visa and Mastercard
- Starting balance support for cards
- Credit and debit transaction tracking
- Auto-categorization for common expense titles
- Secure note field for each card
- Swipe-to-delete card interaction

## Tech Stack

- Python
- Django 5
- SQLite for local development
- HTML, CSS, and JavaScript

## Setup

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run migrations:

```bash
python manage.py migrate
```

4. Start the development server:

```bash
python manage.py runserver
```

5. Open:

```text
http://127.0.0.1:8000/
```

## Usage

- Create an account or sign in.
- Add one or more cards with bank, number, expiry, balance, and optional secure note.
- Add expenses or credits and assign them to a card or cash.
- Open a card and enter your password to reveal full card details and current balance.

## Notes

- `db.sqlite3` is ignored by Git and is intended for local development only.
- CVV is accepted during entry but is not stored.

## Repository

GitHub remote:

```text
https://github.com/mohammed-rihan-c-234/My_Pay.git
```
