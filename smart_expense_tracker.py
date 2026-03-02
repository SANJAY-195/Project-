"""Smart Expense Tracker application.

A lightweight CLI-ready expense tracker that supports:
- Group expense creation with split-by-members support.
- Editing expenses by increasing/decreasing amounts or replacing details.
- Data analysis (member totals, category distribution, monthly trends, and balances).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import argparse
import json
from typing import Dict, List, Optional


@dataclass
class Expense:
    expense_id: int
    title: str
    amount: float
    paid_by: str
    members: List[str]
    category: str = "General"
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    split: Dict[str, float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.amount <= 0:
            raise ValueError("Expense amount must be greater than 0.")
        if not self.members:
            raise ValueError("Members list cannot be empty.")

        if not self.split:
            share = round(self.amount / len(self.members), 2)
            self.split = {member: share for member in self.members}
            # Correct rounding on final member
            difference = round(self.amount - sum(self.split.values()), 2)
            self.split[self.members[-1]] = round(self.split[self.members[-1]] + difference, 2)
        else:
            total = round(sum(self.split.values()), 2)
            if total != round(self.amount, 2):
                raise ValueError("Custom split must sum exactly to expense amount.")


class SmartExpenseTracker:
    def __init__(self) -> None:
        self.members: set[str] = set()
        self.expenses: Dict[int, Expense] = {}
        self._next_id = 1

    def add_member(self, member_name: str) -> None:
        self.members.add(member_name)

    def add_expense(
        self,
        title: str,
        amount: float,
        paid_by: str,
        members: List[str],
        category: str = "General",
        split: Optional[Dict[str, float]] = None,
    ) -> Expense:
        if paid_by not in self.members:
            self.add_member(paid_by)

        for member in members:
            if member not in self.members:
                self.add_member(member)

        expense = Expense(
            expense_id=self._next_id,
            title=title,
            amount=round(amount, 2),
            paid_by=paid_by,
            members=members,
            category=category,
            split=split or {},
        )
        self.expenses[self._next_id] = expense
        self._next_id += 1
        return expense

    def edit_expense(
        self,
        expense_id: int,
        title: Optional[str] = None,
        amount_delta: float = 0,
        category: Optional[str] = None,
    ) -> Expense:
        """Edit an expense by adding/removing amount and updating metadata.

        amount_delta:
          + positive value adds extra amount
          + negative value removes amount
        """
        if expense_id not in self.expenses:
            raise KeyError(f"Expense {expense_id} does not exist.")

        expense = self.expenses[expense_id]

        if title is not None:
            expense.title = title
        if category is not None:
            expense.category = category

        if amount_delta != 0:
            new_amount = round(expense.amount + amount_delta, 2)
            if new_amount <= 0:
                raise ValueError("Edited amount must stay above 0.")
            expense.amount = new_amount
            share = round(expense.amount / len(expense.members), 2)
            expense.split = {member: share for member in expense.members}
            difference = round(expense.amount - sum(expense.split.values()), 2)
            expense.split[expense.members[-1]] = round(expense.split[expense.members[-1]] + difference, 2)

        return expense

    def remove_expense(self, expense_id: int) -> None:
        if expense_id not in self.expenses:
            raise KeyError(f"Expense {expense_id} does not exist.")
        del self.expenses[expense_id]

    def analysis(self) -> Dict[str, object]:
        member_paid: Dict[str, float] = {m: 0.0 for m in self.members}
        member_owed: Dict[str, float] = {m: 0.0 for m in self.members}
        category_totals: Dict[str, float] = {}
        monthly_totals: Dict[str, float] = {}

        for expense in self.expenses.values():
            member_paid[expense.paid_by] = round(member_paid.get(expense.paid_by, 0.0) + expense.amount, 2)
            category_totals[expense.category] = round(category_totals.get(expense.category, 0.0) + expense.amount, 2)

            month_key = datetime.fromisoformat(expense.timestamp).strftime("%Y-%m")
            monthly_totals[month_key] = round(monthly_totals.get(month_key, 0.0) + expense.amount, 2)

            for member, share in expense.split.items():
                member_owed[member] = round(member_owed.get(member, 0.0) + share, 2)

        balances = {
            member: round(member_paid.get(member, 0.0) - member_owed.get(member, 0.0), 2)
            for member in self.members
        }

        return {
            "total_expenses": round(sum(e.amount for e in self.expenses.values()), 2),
            "member_paid": member_paid,
            "member_owed": member_owed,
            "balances": balances,
            "category_totals": category_totals,
            "monthly_totals": dict(sorted(monthly_totals.items())),
            "expense_count": len(self.expenses),
        }

    def save(self, filepath: str) -> None:
        payload = {
            "members": sorted(self.members),
            "next_id": self._next_id,
            "expenses": [
                {
                    "expense_id": e.expense_id,
                    "title": e.title,
                    "amount": e.amount,
                    "paid_by": e.paid_by,
                    "members": e.members,
                    "category": e.category,
                    "timestamp": e.timestamp,
                    "split": e.split,
                }
                for e in self.expenses.values()
            ],
        }
        Path(filepath).write_text(json.dumps(payload, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, filepath: str) -> "SmartExpenseTracker":
        tracker = cls()
        path = Path(filepath)
        if not path.exists():
            return tracker

        data = json.loads(path.read_text(encoding="utf-8"))
        tracker.members = set(data.get("members", []))
        tracker._next_id = data.get("next_id", 1)

        for record in data.get("expenses", []):
            expense = Expense(**record)
            tracker.expenses[expense.expense_id] = expense

        return tracker


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Smart Expense Tracker CLI")
    parser.add_argument("--db", default="expenses.json", help="Path to JSON database file")

    sub = parser.add_subparsers(dest="command", required=True)

    add = sub.add_parser("add-expense", help="Add a new expense")
    add.add_argument("title")
    add.add_argument("amount", type=float)
    add.add_argument("paid_by")
    add.add_argument("members", nargs="+", help="Members included in this split")
    add.add_argument("--category", default="General")

    edit = sub.add_parser("edit-expense", help="Edit an existing expense")
    edit.add_argument("expense_id", type=int)
    edit.add_argument("--title")
    edit.add_argument("--delta", type=float, default=0.0, help="Use + for extra, - for removing amount")
    edit.add_argument("--category")

    remove = sub.add_parser("remove-expense", help="Remove an expense")
    remove.add_argument("expense_id", type=int)

    sub.add_parser("analysis", help="Show analytics summary")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    tracker = SmartExpenseTracker.load(args.db)

    if args.command == "add-expense":
        expense = tracker.add_expense(
            title=args.title,
            amount=args.amount,
            paid_by=args.paid_by,
            members=args.members,
            category=args.category,
        )
        tracker.save(args.db)
        print(f"Added expense #{expense.expense_id}: {expense.title} ({expense.amount})")

    elif args.command == "edit-expense":
        expense = tracker.edit_expense(
            expense_id=args.expense_id,
            title=args.title,
            amount_delta=args.delta,
            category=args.category,
        )
        tracker.save(args.db)
        print(f"Updated expense #{expense.expense_id}: amount={expense.amount}, category={expense.category}")

    elif args.command == "remove-expense":
        tracker.remove_expense(args.expense_id)
        tracker.save(args.db)
        print(f"Removed expense #{args.expense_id}")

    elif args.command == "analysis":
        report = tracker.analysis()
        print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
