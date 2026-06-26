#!/usr/bin/env python3
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, filters, ContextTypes
)

from config import TOKEN
from database import Database
from handlers import (
    set_db, start, handle_message,
    summary, total, list_expenses, delete_expense, date_range,
    stats, categories, budget, export_command, export_csv,
    export_excel, export_pdf, reset, achievements, fun_fact,
    search, dashboard, reminder, daily_limit, help_command,
    list_commands, goals, wishlist, button_handler, edit_expense
)
from scheduler import setup_scheduler

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

REPLY_BUTTON_MAP = {
    "➕ Add Expense": "add_expense",
    "📊 Analytics": "analytics_menu",
    "💰 Budget": "budget_menu",
    "📅 Reports": "reports_menu",
    "🏆 Achievements": "show_achievements",
    "⚙️ Settings": "settings_menu",
    "❓ Help": "help_menu",
}

async def reply_keyboard_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if text in REPLY_BUTTON_MAP:
        callback_data = REPLY_BUTTON_MAP[text]
        user_id = update.effective_user.id
        from keyboards import main_menu_keyboard
        if callback_data == "add_expense":
            await update.message.reply_text(
                "➕ *Add Expense*\n\nSend an expense in any format:\n"
                "`200 lunch`\n`spent 500 on food`\n`Coffee 150`",
                parse_mode="Markdown"
            )
        else:
            from handlers import button_handler as bh
            from telegram import CallbackQuery
            await update.message.reply_text(
                "Use the inline buttons below:",
                reply_markup=main_menu_keyboard()
            )
        return True
    return False

async def message_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await reply_keyboard_handler(update, context):
        return
    await handle_message(update, context)

async def post_init(application: Application):
    from config import DB_PATH
    db = Database(DB_PATH)
    application.bot_data["db"] = db
    set_db(db)
    logger.info(f"Database initialized at {DB_PATH}")

def main():
    app = Application.builder().token(TOKEN).post_init(post_init).build()

    # Command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("summary", summary))
    app.add_handler(CommandHandler("total", total))
    app.add_handler(CommandHandler("list", list_expenses))
    app.add_handler(CommandHandler("delete", delete_expense))
    app.add_handler(CommandHandler("from", date_range))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("categories", categories))
    app.add_handler(CommandHandler("budget", budget))
    app.add_handler(CommandHandler("export", export_command))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(CommandHandler("achievements", achievements))
    app.add_handler(CommandHandler("fact", fun_fact))
    app.add_handler(CommandHandler("search", search))
    app.add_handler(CommandHandler("dashboard", dashboard))
    app.add_handler(CommandHandler("reminder", reminder))
    app.add_handler(CommandHandler("dailylimit", daily_limit))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("commands", list_commands))
    app.add_handler(CommandHandler("goals", goals))
    app.add_handler(CommandHandler("wishlist", wishlist))
    app.add_handler(CommandHandler("edit", edit_expense))

    # Callback query handlers
    app.add_handler(CallbackQueryHandler(button_handler))

    # Message handler (text, no commands)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_router))

    # Scheduler
    setup_scheduler(app)

    logger.info("Bot started!")
    app.run_polling()

if __name__ == "__main__":
    main()
