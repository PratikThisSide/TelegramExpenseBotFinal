import logging
from datetime import time, date, timedelta
from telegram.ext import ContextTypes
from utils import get_category_emoji

logger = logging.getLogger(__name__)

async def daily_reminder_job(context: ContextTypes.DEFAULT_TYPE):
    db = context.application.bot_data.get("db")
    if not db:
        return
    reminders = db.get_all_reminders()
    for row in reminders:
        user_id = row["user_id"]
        daily_limit = row["daily_limit"]
        today_total = db.get_today_total(user_id)
        if today_total > daily_limit:
            top_cat_data = db.get_monthly_summary(user_id)
            top_cat = top_cat_data[0]["category"] if top_cat_data else "Unknown"
            emoji = get_category_emoji(top_cat)
            msg = (
                f"⚠️ *Spending Alert!*\n\n"
                f"You've spent *{today_total:,.0f}* today.\n"
                f"Your daily limit is *{daily_limit:,.0f}*.\n"
                f"Over Budget: *{today_total - daily_limit:,.0f}*\n\n"
                f"Top Category:\n"
                f"{get_category_emoji(top_cat)} {top_cat}\n\n"
                f"💡 Tip: Try reducing expenses tomorrow!"
            )
        else:
            msg = (
                f"✅ *Great job!*\n\n"
                f"Today's spending: *{today_total:,.0f}*\n"
                f"Daily limit: *{daily_limit:,.0f}*\n"
                f"Remaining: *{daily_limit - today_total:,.0f}*\n\n"
                f"You stayed within your daily budget. Keep it up! 🎉"
            )
        try:
            await context.bot.send_message(chat_id=user_id, text=msg, parse_mode="Markdown")
        except Exception as e:
            logger.error(f"Failed to send reminder to {user_id}: {e}")

async def monthly_report_job(context: ContextTypes.DEFAULT_TYPE):
    today = date.today()
    if today.day != 1:
        return
    db = context.application.bot_data.get("db")
    if not db:
        return
    user_ids = set()
    for row in db.cursor.execute("SELECT DISTINCT user_id FROM expenses").fetchall():
        user_ids.add(row["user_id"])
    for row in db.cursor.execute("SELECT DISTINCT user_id FROM settings").fetchall():
        user_ids.add(row["user_id"])
    for user_id in user_ids:
        total = db.get_monthly_total(user_id)
        if total == 0:
            continue
        stats = db.get_stats(user_id)
        data = db.get_monthly_summary(user_id)
        top_cat = data[0]["category"] if data else "N/A"
        top_amt = data[0]["total"] if data else 0
        count = stats["count"]
        avg = stats["avg"]
        biggest = stats["biggest"]
        msg = (
            f"📊 *Monthly Report*\n\n"
            f"Total Spent: *{total:,.0f}*\n"
            f"Biggest Category: {get_category_emoji(top_cat)} {top_cat} ({top_amt:,.0f})\n"
            f"Highest Expense: *{biggest:,.0f}*\n"
            f"Average/Day: *{avg:,.0f}*\n"
            f"Transactions: *{count}*\n\n"
            f"Keep tracking! 🎯"
        )
        try:
            await context.bot.send_message(chat_id=user_id, text=msg, parse_mode="Markdown")
        except Exception as e:
            logger.error(f"Failed to send monthly report to {user_id}: {e}")

async def weekly_report_job(context: ContextTypes.DEFAULT_TYPE):
    db = context.application.bot_data.get("db")
    if not db:
        return
    user_ids = set()
    for row in db.cursor.execute("SELECT DISTINCT user_id FROM expenses").fetchall():
        user_ids.add(row["user_id"])
    for user_id in user_ids:
        week_expenses = db.get_this_week_expenses(user_id)
        if not week_expenses:
            continue
        total = sum(r["amount"] for r in week_expenses)
        day_totals = {}
        for r in week_expenses:
            d = r["date"][:10]
            day_totals[d] = day_totals.get(d, 0) + r["amount"]
        max_day = max(day_totals, key=day_totals.get)
        max_day_name = date.fromisoformat(max_day).strftime("%A")
        cat_totals = {}
        for r in week_expenses:
            cat_totals[r["category"]] = cat_totals.get(r["category"], 0) + r["amount"]
        top_cat = max(cat_totals, key=cat_totals.get) if cat_totals else "N/A"
        msg = (
            f"📅 *Weekly Report*\n\n"
            f"Week Total: *{total:,.0f}*\n"
            f"Highest Day: *{max_day_name}*\n"
            f"Top Category: {get_category_emoji(top_cat)} {top_cat}\n\n"
            f"💡 Tip: Review your weekly spending and plan ahead!"
        )
        try:
            await context.bot.send_message(chat_id=user_id, text=msg, parse_mode="Markdown")
        except Exception as e:
            logger.error(f"Weekly report error for {user_id}: {e}")

def setup_scheduler(application):
    job_queue = application.job_queue
    if job_queue is None:
        logger.warning("JobQueue not available - scheduled tasks disabled")
        return
    job_queue.run_daily(daily_reminder_job, time=time(21, 0), name="daily_reminder")
    job_queue.run_daily(monthly_report_job, time=time(9, 0), name="monthly_report")
    job_queue.run_daily(weekly_report_job, time=time(20, 0), days=(6,), name="weekly_report")
    logger.info("Scheduler started: daily reminder (21:00), monthly report (1st @ 9:00), weekly report (Sun 20:00)")
