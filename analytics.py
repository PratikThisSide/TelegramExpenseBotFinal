import io
import os
import logging
from datetime import date, timedelta
from utils import format_currency, get_category_emoji, progress_bar

logger = logging.getLogger(__name__)

HAS_MATPLOTLIB = False
try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.ticker as mticker
    import numpy as np
    HAS_MATPLOTLIB = True
except ImportError:
    logger.warning("matplotlib not available - charts disabled")

def generate_pie_chart(db, user_id):
    if not HAS_MATPLOTLIB:
        return None
    try:
        data = db.get_monthly_summary(user_id)
        if not data:
            return None
        labels = [r["category"] for r in data]
        values = [r["total"] for r in data]
        colors = plt.cm.Pastel1(np.linspace(0, 1, len(labels)))
        fig, ax = plt.subplots(figsize=(6, 6))
        wedges, texts, autotexts = ax.pie(
            values, labels=None, autopct="%1.1f%%",
            startangle=90, colors=colors, pctdistance=0.85
        )
        for t in autotexts:
            t.set_fontsize(9)
        ax.legend(wedges, labels, title="Categories", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1), fontsize=8)
        ax.set_title("Monthly Spending Breakdown", fontsize=14, fontweight="bold")
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=150, bbox_inches="tight")
        buf.seek(0)
        plt.close(fig)
        return buf
    except Exception as e:
        logger.error(f"Pie chart error: {e}")
        return None

def generate_line_chart(db, user_id):
    if not HAS_MATPLOTLIB:
        return None
    try:
        data = db.get_daily_totals_for_month(user_id)
        if not data:
            return None
        days = [r["day"][-2:] for r in data]
        totals = [r["total"] for r in data]
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(range(len(days)), totals, marker="o", linestyle="-", color="#4CAF50", linewidth=2, markersize=6)
        ax.fill_between(range(len(days)), totals, alpha=0.2, color="#4CAF50")
        ax.set_xticks(range(len(days)))
        ax.set_xticklabels(days, fontsize=9)
        ax.set_xlabel("Day of Month", fontsize=10)
        ax.set_ylabel("Amount (₹)", fontsize=10)
        ax.set_title("Daily Spending Trend", fontsize=14, fontweight="bold")
        ax.grid(axis="y", alpha=0.3)
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=150, bbox_inches="tight")
        buf.seek(0)
        plt.close(fig)
        return buf
    except Exception as e:
        logger.error(f"Line chart error: {e}")
        return None

def generate_bar_chart(db, user_id):
    if not HAS_MATPLOTLIB:
        return None
    try:
        data = db.get_monthly_summary(user_id)
        if not data:
            return None
        categories = [r["category"] for r in data]
        values = [r["total"] for r in data]
        colors = plt.cm.Set3(np.linspace(0, 1, len(categories)))
        fig, ax = plt.subplots(figsize=(8, 5))
        bars = ax.bar(categories, values, color=colors, edgecolor="white", linewidth=1.5)
        for bar, val in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + max(values) * 0.01,
                    f"₹{val:,.0f}", ha="center", va="bottom", fontsize=9, fontweight="bold")
        ax.set_xlabel("Category", fontsize=11)
        ax.set_ylabel("Amount (₹)", fontsize=11)
        ax.set_title("Category-wise Spending", fontsize=14, fontweight="bold")
        plt.xticks(rotation=30, ha="right", fontsize=9)
        ax.grid(axis="y", alpha=0.3)
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=150, bbox_inches="tight")
        buf.seek(0)
        plt.close(fig)
        return buf
    except Exception as e:
        logger.error(f"Bar chart error: {e}")
        return None

def generate_monthly_trend_chart(db, user_id):
    if not HAS_MATPLOTLIB:
        return None
    try:
        data = db.get_daily_totals_for_month(user_id)
        if not data:
            return None
        days = [r["day"] for r in data]
        totals = [r["total"] for r in data]
        labels = [d[-2:] for d in days]
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.fill_between(range(len(days)), totals, alpha=0.3, color="#2196F3")
        ax.plot(range(len(days)), totals, color="#1976D2", linewidth=2, marker="o", markersize=5)
        avg = np.mean(totals) if totals else 0
        ax.axhline(y=avg, color="red", linestyle="--", linewidth=1, label=f"Avg: ₹{avg:.0f}")
        ax.set_xticks(range(len(days)))
        ax.set_xticklabels(labels, fontsize=8, rotation=45)
        ax.set_xlabel("Day", fontsize=10)
        ax.set_ylabel("Amount (₹)", fontsize=10)
        ax.set_title("Monthly Spending Trend", fontsize=14, fontweight="bold")
        ax.legend(fontsize=9)
        ax.grid(alpha=0.3)
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=150, bbox_inches="tight")
        buf.seek(0)
        plt.close(fig)
        return buf
    except Exception as e:
        logger.error(f"Trend chart error: {e}")
        return None

def get_smart_suggestions(db, user_id):
    suggestions = []
    monthly = db.get_monthly_summary(user_id)
    if not monthly:
        return ["Start tracking expenses to get suggestions!"]
    total = sum(r["total"] for r in monthly)
    for r in monthly:
        pct = (r["total"] / total * 100) if total > 0 else 0
        if pct > 30:
            suggestions.append(
                f"You spent {pct:.0f}% on {r['category']}. "
                f"Consider setting a budget for {r['category']}."
            )
    week_data = db.get_this_week_expenses(user_id)
    if week_data:
        day_totals = {}
        for r in week_data:
            d = r["date"][:10]
            day_totals[d] = day_totals.get(d, 0) + r["amount"]
        if day_totals:
            max_day = max(day_totals, key=day_totals.get)
            dt = date.fromisoformat(max_day)
            suggestions.append(f"Your highest spending day this week was {dt.strftime('%A')}.")
    count = db.get_expense_count(user_id)
    if count > 0:
        suggestions.append(f"You've logged {count} total expenses. Keep it up!")
    if not suggestions:
        suggestions.append("Great work staying on track!")
    return suggestions

def get_detailed_stats(db, user_id):
    stats = db.get_stats(user_id)
    if not stats or stats["count"] == 0:
        return None
    month_total = stats["total"]
    count = stats["count"]
    avg = stats["avg"]
    biggest = stats["biggest"]
    today_count = len(db.get_today_expenses(user_id))
    today_total = db.get_today_total(user_id)
    week_total = db.get_this_week_total(user_id)
    return {
        "month_total": month_total,
        "count": count,
        "avg": avg,
        "biggest": biggest,
        "today_count": today_count,
        "today_total": today_total,
        "week_total": week_total,
    }
