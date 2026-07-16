import sqlite3
import logging
from datetime import date, datetime, timedelta
from config import DB_PATH

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_path=DB_PATH):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        self.cursor.executescript("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                amount REAL,
                category TEXT,
                date TEXT,
                tags TEXT DEFAULT '',
                note TEXT DEFAULT ''
            );
  

            CREATE TABLE IF NOT EXISTS budgets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                category TEXT,
                amount REAL,
                month TEXT,
                UNIQUE(user_id, category, month)
            );

            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE,
                enabled INTEGER DEFAULT 1,
                reminder_time TEXT DEFAULT '21:00',
                daily_limit REAL DEFAULT 500
            );

            CREATE TABLE IF NOT EXISTS goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                name TEXT,
                target REAL,
                saved REAL DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS wishlist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                name TEXT,
                price REAL,
                saved REAL DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS achievements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                name TEXT,
                unlocked_at TEXT,
                UNIQUE(user_id, name)
            );

            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE,
                currency TEXT DEFAULT '₹',
                daily_limit REAL DEFAULT 500,
                reminder_time TEXT DEFAULT '21:00',
                dark_mode INTEGER DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS streaks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE,
                current_streak INTEGER DEFAULT 0,
                longest_streak INTEGER DEFAULT 0,
                last_date TEXT,
                xp INTEGER DEFAULT 0,
                level INTEGER DEFAULT 1
            );
        """)
        self.conn.commit()

    # ----- Expenses -----
    def add_expense(self, user_id, amount, category, tags="", note=""):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute(
            "INSERT INTO expenses (amount, category, date, user_id, tags, note) VALUES (?, ?, ?, ?, ?, ?)",
            (amount, category, now, user_id, tags, note)
        )
        self.conn.commit()
        self._update_streaks(user_id)
        self._add_xp(user_id, 10)
        return self.cursor.lastrowid

    def get_expense(self, expense_id, user_id):
        self.cursor.execute(
            "SELECT * FROM expenses WHERE id = ? AND user_id = ?",
            (expense_id, user_id)
        )
        return self.cursor.fetchone()

    def get_all_expenses(self, user_id, limit=20):
        self.cursor.execute(
            "SELECT id, amount, category, date, tags FROM expenses WHERE user_id = ? ORDER BY date DESC, id DESC LIMIT ?",
            (user_id, limit)
        )
        return self.cursor.fetchall()

    def delete_expense(self, expense_id, user_id):
        self.cursor.execute(
            "DELETE FROM expenses WHERE id = ? AND user_id = ?",
            (expense_id, user_id)
        )
        self.conn.commit()
        return self.cursor.rowcount > 0

    def update_expense(self, expense_id, user_id, amount=None, category=None):
        expense = self.get_expense(expense_id, user_id)
        if not expense:
            return False
        new_amount = amount if amount is not None else expense["amount"]
        new_cat = category if category is not None else expense["category"]
        self.cursor.execute(
            "UPDATE expenses SET amount = ?, category = ? WHERE id = ? AND user_id = ?",
            (new_amount, new_cat, expense_id, user_id)
        )
        self.conn.commit()
        return True

    def get_expenses_by_date_range(self, user_id, start_date, end_date):
        self.cursor.execute(
            "SELECT id, amount, category, date, tags FROM expenses WHERE user_id = ? AND date >= ? AND date <= ? ORDER BY date DESC",
            (user_id, start_date, end_date)
        )
        return self.cursor.fetchall()

    def search_expenses(self, user_id, query):
        like = f"%{query}%"
        self.cursor.execute(
            "SELECT id, amount, category, date, tags FROM expenses WHERE user_id = ? AND (category LIKE ? OR tags LIKE ? OR note LIKE ?) ORDER BY date DESC LIMIT 20",
            (user_id, like, like, like)
        )
        return self.cursor.fetchall()

    def get_today_expenses(self, user_id):
        today = date.today().isoformat()
        self.cursor.execute(
            "SELECT amount, category FROM expenses WHERE user_id = ? AND substr(date, 1, 10) = ?",
            (user_id, today)
        )
        return self.cursor.fetchall()

    def get_today_total(self, user_id):
        today = date.today().isoformat()
        self.cursor.execute(
            "SELECT COALESCE(SUM(amount), 0) FROM expenses WHERE user_id = ? AND substr(date, 1, 10) = ?",
            (user_id, today)
        )
        return self.cursor.fetchone()[0]

    def get_this_week_expenses(self, user_id):
        today = date.today()
        start = today - timedelta(days=today.weekday())
        self.cursor.execute(
            "SELECT amount, category, date FROM expenses WHERE user_id = ? AND substr(date, 1, 10) >= ? ORDER BY date",
            (user_id, start.isoformat())
        )
        return self.cursor.fetchall()

    def get_this_week_total(self, user_id):
        today = date.today()
        start = today - timedelta(days=today.weekday())
        self.cursor.execute(
            "SELECT COALESCE(SUM(amount), 0) FROM expenses WHERE user_id = ? AND substr(date, 1, 10) >= ?",
            (user_id, start.isoformat())
        )
        return self.cursor.fetchone()[0]

    def get_month_start(self):
        return date.today().replace(day=1).isoformat()

    def get_monthly_summary(self, user_id):
        month_start = self.get_month_start()
        self.cursor.execute(
            "SELECT category, SUM(amount) as total FROM expenses WHERE user_id = ? AND substr(date, 1, 10) >= ? GROUP BY category ORDER BY total DESC",
            (user_id, month_start)
        )
        return self.cursor.fetchall()

    def get_monthly_total(self, user_id):
        month_start = self.get_month_start()
        self.cursor.execute(
            "SELECT COALESCE(SUM(amount), 0) FROM expenses WHERE user_id = ? AND substr(date, 1, 10) >= ?",
            (user_id, month_start)
        )
        return self.cursor.fetchone()[0]

    def get_stats(self, user_id):
        month_start = self.get_month_start()
        self.cursor.execute(
            "SELECT COUNT(*) as count, COALESCE(SUM(amount), 0) as total, COALESCE(MAX(amount), 0) as biggest, COALESCE(AVG(amount), 0) as avg FROM expenses WHERE user_id = ? AND substr(date, 1, 10) >= ?",
            (user_id, month_start)
        )
        return self.cursor.fetchone()

    def get_categories(self, user_id):
        self.cursor.execute(
            "SELECT DISTINCT category FROM expenses WHERE user_id = ? ORDER BY category",
            (user_id,)
        )
        return [row["category"] for row in self.cursor.fetchall()]

    def get_category_total(self, user_id, category):
        month_start = self.get_month_start()
        self.cursor.execute(
            "SELECT COALESCE(SUM(amount), 0) FROM expenses WHERE user_id = ? AND category = ? AND substr(date, 1, 10) >= ?",
            (user_id, category, month_start)
        )
        return self.cursor.fetchone()[0]

    def get_daily_totals_for_month(self, user_id):
        month_start = self.get_month_start()
        self.cursor.execute(
            "SELECT substr(date, 1, 10) as day, SUM(amount) as total FROM expenses WHERE user_id = ? AND substr(date, 1, 10) >= ? GROUP BY day ORDER BY day",
            (user_id, month_start)
        )
        return self.cursor.fetchall()

    def delete_all_expenses(self, user_id):
        self.cursor.execute("DELETE FROM expenses WHERE user_id = ?", (user_id,))
        self.cursor.execute("DELETE FROM achievements WHERE user_id = ?", (user_id,))
        self.conn.commit()

    def get_expense_count(self, user_id):
        self.cursor.execute("SELECT COUNT(*) FROM expenses WHERE user_id = ?", (user_id,))
        return self.cursor.fetchone()[0]

    # ----- Budgets -----
    def set_budget(self, user_id, category, amount):
        month = date.today().replace(day=1).isoformat()
        self.cursor.execute(
            "INSERT OR REPLACE INTO budgets (user_id, category, amount, month) VALUES (?, ?, ?, ?)",
            (user_id, category, amount, month)
        )
        self.conn.commit()

    def get_budgets(self, user_id):
        month = date.today().replace(day=1).isoformat()
        self.cursor.execute(
            "SELECT category, amount FROM budgets WHERE user_id = ? AND month = ?",
            (user_id, month)
        )
        return self.cursor.fetchall()

    def get_budget_for_category(self, user_id, category):
        month = date.today().replace(day=1).isoformat()
        self.cursor.execute(
            "SELECT amount FROM budgets WHERE user_id = ? AND category = ? AND month = ?",
            (user_id, category, month)
        )
        row = self.cursor.fetchone()
        return row["amount"] if row else None

    def delete_budget(self, user_id, category):
        month = date.today().replace(day=1).isoformat()
        self.cursor.execute(
            "DELETE FROM budgets WHERE user_id = ? AND category = ? AND month = ?",
            (user_id, category, month)
        )
        self.conn.commit()

    # ----- Reminders -----
    def get_reminder(self, user_id):
        self.cursor.execute(
            "SELECT * FROM reminders WHERE user_id = ?",
            (user_id,)
        )
        return self.cursor.fetchone()

    def set_reminder(self, user_id, enabled=None, reminder_time=None, daily_limit=None):
        existing = self.get_reminder(user_id)
        if existing:
            if enabled is not None:
                self.cursor.execute("UPDATE reminders SET enabled = ? WHERE user_id = ?", (enabled, user_id))
            if reminder_time is not None:
                self.cursor.execute("UPDATE reminders SET reminder_time = ? WHERE user_id = ?", (reminder_time, user_id))
            if daily_limit is not None:
                self.cursor.execute("UPDATE reminders SET daily_limit = ? WHERE user_id = ?", (daily_limit, user_id))
        else:
            self.cursor.execute(
                "INSERT INTO reminders (user_id, enabled, reminder_time, daily_limit) VALUES (?, ?, ?, ?)",
                (user_id, 1 if enabled is None else enabled, reminder_time or "21:00", daily_limit or 500)
            )
        self.conn.commit()

    def set_daily_limit(self, user_id, limit):
        self.set_reminder(user_id, daily_limit=limit)

    def get_all_reminders(self):
        self.cursor.execute("SELECT user_id, reminder_time, daily_limit FROM reminders WHERE enabled = 1")
        return self.cursor.fetchall()

    # ----- Settings -----
    def get_setting(self, user_id, key):
        self.cursor.execute("SELECT * FROM settings WHERE user_id = ?", (user_id,))
        row = self.cursor.fetchone()
        if not row:
            self.cursor.execute("INSERT INTO settings (user_id) VALUES (?)", (user_id,))
            self.conn.commit()
            self.cursor.execute("SELECT * FROM settings WHERE user_id = ?", (user_id,))
            row = self.cursor.fetchone()
        return row[key] if row else None

    def set_setting(self, user_id, key, value):
        existing = self.cursor.execute("SELECT user_id FROM settings WHERE user_id = ?", (user_id,)).fetchone()
        if existing:
            self.cursor.execute(f"UPDATE settings SET {key} = ? WHERE user_id = ?", (value, user_id))
        else:
            self.cursor.execute(f"INSERT INTO settings (user_id, {key}) VALUES (?, ?)", (user_id, value))
        self.conn.commit()

    # ----- Goals -----
    def add_goal(self, user_id, name, target):
        self.cursor.execute(
            "INSERT INTO goals (user_id, name, target) VALUES (?, ?, ?)",
            (user_id, name, target)
        )
        self.conn.commit()

    def get_goals(self, user_id):
        self.cursor.execute("SELECT * FROM goals WHERE user_id = ?", (user_id,))
        return self.cursor.fetchall()

    def add_goal_savings(self, goal_id, user_id, amount):
        self.cursor.execute(
            "UPDATE goals SET saved = saved + ? WHERE id = ? AND user_id = ?",
            (amount, goal_id, user_id)
        )
        self.conn.commit()

    def delete_goal(self, goal_id, user_id):
        self.cursor.execute("DELETE FROM goals WHERE id = ? AND user_id = ?", (goal_id, user_id))
        self.conn.commit()

    # ----- Wishlist -----
    def add_wishlist_item(self, user_id, name, price):
        self.cursor.execute(
            "INSERT INTO wishlist (user_id, name, price) VALUES (?, ?, ?)",
            (user_id, name, price)
        )
        self.conn.commit()

    def get_wishlist(self, user_id):
        self.cursor.execute("SELECT * FROM wishlist WHERE user_id = ?", (user_id,))
        return self.cursor.fetchall()

    def add_wishlist_savings(self, item_id, user_id, amount):
        self.cursor.execute(
            "UPDATE wishlist SET saved = saved + ? WHERE id = ? AND user_id = ?",
            (amount, item_id, user_id)
        )
        self.conn.commit()

    def delete_wishlist_item(self, item_id, user_id):
        self.cursor.execute("DELETE FROM wishlist WHERE id = ? AND user_id = ?", (item_id, user_id))
        self.conn.commit()

    # ----- Achievements -----
    def unlock_achievement(self, user_id, name):
        now = datetime.now().isoformat()
        try:
            self.cursor.execute(
                "INSERT INTO achievements (user_id, name, unlocked_at) VALUES (?, ?, ?)",
                (user_id, name, now)
            )
            self.conn.commit()
            self._add_xp(user_id, 50)
            return True
        except sqlite3.IntegrityError:
            return False

    def get_achievements(self, user_id):
        self.cursor.execute("SELECT name, unlocked_at FROM achievements WHERE user_id = ?", (user_id,))
        return self.cursor.fetchall()

    # ----- Streaks & XP -----
    def _update_streaks(self, user_id):
        today = date.today()
        self.cursor.execute("SELECT * FROM streaks WHERE user_id = ?", (user_id,))
        row = self.cursor.fetchone()
        if not row:
            self.cursor.execute(
                "INSERT INTO streaks (user_id, current_streak, longest_streak, last_date, xp, level) VALUES (?, 1, 1, ?, 10, 1)",
                (user_id, today.isoformat())
            )
            self.conn.commit()
            return
        last = row["last_date"]
        if last == today.isoformat():
            return
        yesterday = (today - timedelta(days=1)).isoformat()
        if last == yesterday:
            new_streak = row["current_streak"] + 1
            longest = max(new_streak, row["longest_streak"])
        else:
            new_streak = 1
            longest = row["longest_streak"]
        self.cursor.execute(
            "UPDATE streaks SET current_streak = ?, longest_streak = ?, last_date = ? WHERE user_id = ?",
            (new_streak, longest, today.isoformat(), user_id)
        )
        self.conn.commit()

    def _add_xp(self, user_id, amount):
        self.cursor.execute("SELECT xp, level FROM streaks WHERE user_id = ?", (user_id,))
        row = self.cursor.fetchone()
        if not row:
            return
        new_xp = row["xp"] + amount
        new_level = (new_xp // 100) + 1
        self.cursor.execute(
            "UPDATE streaks SET xp = ?, level = ? WHERE user_id = ?",
            (new_xp, new_level, user_id)
        )
        self.conn.commit()

    def get_streaks(self, user_id):
        self.cursor.execute("SELECT * FROM streaks WHERE user_id = ?", (user_id,))
        return self.cursor.fetchone()

    # ----- Export -----
    def export_csv(self, user_id):
        self.cursor.execute(
            "SELECT id, amount, category, date, tags, note FROM expenses WHERE user_id = ? ORDER BY date DESC",
            (user_id,)
        )
        rows = self.cursor.fetchall()
        csv = "id,amount,category,date,tags,note\n"
        for r in rows:
            csv += f"{r['id']},{r['amount']},{r['category']},{r['date']},{r['tags']},{r['note']}\n"
        return csv

    def export_all_data(self, user_id):
        return {
            "expenses": self.cursor.execute("SELECT * FROM expenses WHERE user_id = ? ORDER BY date DESC", (user_id,)).fetchall(),
            "budgets": self.get_budgets(user_id),
            "goals": self.get_goals(user_id),
            "wishlist": self.get_wishlist(user_id),
            "achievements": self.get_achievements(user_id),
            "settings": self.cursor.execute("SELECT * FROM settings WHERE user_id = ?", (user_id,)).fetchone(),
        }
