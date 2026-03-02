# Smart Expense Tracker

Smart Expense Tracker is a Python-based application for managing group expenses.
It supports:

- Adding expenses and splitting them among group members.
- Editing expenses by increasing or decreasing amount (extra added or removed).
- Removing expenses.
- Running data analysis for totals, balances, categories, and monthly trends.

## Requirements

- Python 3.10+

## Quick Start

```bash
python smart_expense_tracker.py --help
```

### Add expense

```bash
python smart_expense_tracker.py add-expense "Dinner" 120 Alice Alice Bob Carol --category Food
```

### Edit expense (add extra 30)

```bash
python smart_expense_tracker.py edit-expense 1 --delta 30
```

### Edit expense (remove 20)

```bash
python smart_expense_tracker.py edit-expense 1 --delta -20
```

### Remove expense

```bash
python smart_expense_tracker.py remove-expense 1
```

### Analytics

```bash
python smart_expense_tracker.py analysis
```

By default the app stores data in `expenses.json`. Use `--db <file>` to use a different file.

## Example Analysis Output

```json
{
  "total_expenses": 460.0,
  "member_paid": {
    "Alice": 300.0,
    "Bob": 160.0
  },
  "member_owed": {
    "Alice": 230.0,
    "Bob": 230.0
  },
  "balances": {
    "Alice": 70.0,
    "Bob": -70.0
  },
  "category_totals": {
    "Food": 120.0,
    "Travel": 340.0
  },
  "monthly_totals": {
    "2026-03": 460.0
  },
  "expense_count": 2
}
```
