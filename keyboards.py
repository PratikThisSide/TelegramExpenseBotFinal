from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# ----- Reply Keyboard (Main Menu) -----
def main_reply_keyboard():
    buttons = [
        [KeyboardButton("➕ Add Expense"), KeyboardButton("📊 Analytics")],
        [KeyboardButton("💰 Budget"), KeyboardButton("📅 Reports")],
        [KeyboardButton("🏆 Achievements"), KeyboardButton("⚙️ Settings")],
        [KeyboardButton("❓ Help")],
    ]
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)

# ----- Inline Keyboards -----
def main_menu_keyboard():
    buttons = [
        [InlineKeyboardButton("➕ Add Expense", callback_data="add_expense")],
        [InlineKeyboardButton("📊 Analytics", callback_data="analytics_menu"),
         InlineKeyboardButton("💰 Budget", callback_data="budget_menu")],
        [InlineKeyboardButton("📅 Reports", callback_data="reports_menu"),
         InlineKeyboardButton("🏆 Achievements", callback_data="show_achievements")],
        [InlineKeyboardButton("⚙️ Settings", callback_data="settings_menu"),
         InlineKeyboardButton("❓ Help", callback_data="help_menu")],
    ]
    return InlineKeyboardMarkup(buttons)

def analytics_keyboard():
    buttons = [
        [InlineKeyboardButton("📊 Today", callback_data="analytics_today"),
         InlineKeyboardButton("📅 This Week", callback_data="analytics_week")],
        [InlineKeyboardButton("📆 This Month", callback_data="analytics_month"),
         InlineKeyboardButton("📁 Last Month", callback_data="analytics_lastmonth")],
        [InlineKeyboardButton("📅 Custom Date", callback_data="analytics_custom")],
        [InlineKeyboardButton("🔙 Back", callback_data="main_menu")],
    ]
    return InlineKeyboardMarkup(buttons)

def reports_keyboard():
    buttons = [
        [InlineKeyboardButton("📊 Pie Chart", callback_data="chart_pie"),
         InlineKeyboardButton("📈 Line Chart", callback_data="chart_line")],
        [InlineKeyboardButton("📊 Bar Chart", callback_data="chart_bar"),
         InlineKeyboardButton("📅 Monthly Trend", callback_data="chart_trend")],
        [InlineKeyboardButton("🔙 Back", callback_data="main_menu")],
    ]
    return InlineKeyboardMarkup(buttons)

def budget_menu_keyboard():
    buttons = [
        [InlineKeyboardButton("📋 Show Budgets", callback_data="budget_show"),
         InlineKeyboardButton("✏️ Set Budget", callback_data="budget_set")],
        [InlineKeyboardButton("🗑 Delete Budget", callback_data="budget_delete")],
        [InlineKeyboardButton("🔙 Back", callback_data="main_menu")],
    ]
    return InlineKeyboardMarkup(buttons)

def settings_keyboard():
    buttons = [
        [InlineKeyboardButton("💰 Daily Limit", callback_data="setting_dailylimit"),
         InlineKeyboardButton("⏰ Reminder Time", callback_data="setting_remindertime")],
        [InlineKeyboardButton("🔄 Currency", callback_data="setting_currency"),
         InlineKeyboardButton("🌙 Dark Mode", callback_data="setting_darkmode")],
        [InlineKeyboardButton("🔙 Back", callback_data="main_menu")],
    ]
    return InlineKeyboardMarkup(buttons)

def help_keyboard():
    buttons = [
        [InlineKeyboardButton("💸 Expense", callback_data="help_expense")],
        [InlineKeyboardButton("💰 Budget", callback_data="help_budget"),
         InlineKeyboardButton("📊 Reports", callback_data="help_reports")],
        [InlineKeyboardButton("⚙️ Settings", callback_data="help_settings"),
         InlineKeyboardButton("🏆 Achievements", callback_data="help_achievements")],
        [InlineKeyboardButton("🔙 Back", callback_data="main_menu")],
    ]
    return InlineKeyboardMarkup(buttons)

def expense_confirmation_keyboard(expense_id):
    buttons = [
        [InlineKeyboardButton("↩️ Undo", callback_data=f"undo_{expense_id}"),
         InlineKeyboardButton("✏️ Edit", callback_data=f"edit_{expense_id}")],
        [InlineKeyboardButton("➕ Add Another", callback_data="add_expense")],
        [InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")],
    ]
    return InlineKeyboardMarkup(buttons)

def goals_keyboard():
    buttons = [
        [InlineKeyboardButton("🎯 New Goal", callback_data="goal_add")],
        [InlineKeyboardButton("📋 View Goals", callback_data="goal_view")],
        [InlineKeyboardButton("🔙 Back", callback_data="main_menu")],
    ]
    return InlineKeyboardMarkup(buttons)

def reminder_keyboard():
    buttons = [
        [InlineKeyboardButton("🔔 Reminder On", callback_data="reminder_on"),
         InlineKeyboardButton("🔕 Reminder Off", callback_data="reminder_off")],
        [InlineKeyboardButton("⏰ Set Time", callback_data="reminder_time")],
        [InlineKeyboardButton("🔙 Back", callback_data="settings_menu")],
    ]
    return InlineKeyboardMarkup(buttons)

def export_keyboard():
    buttons = [
        [InlineKeyboardButton("📄 CSV", callback_data="export_csv"),
         InlineKeyboardButton("📊 Excel", callback_data="export_excel")],
        [InlineKeyboardButton("📑 PDF", callback_data="export_pdf")],
        [InlineKeyboardButton("🔙 Back", callback_data="main_menu")],
    ]
    return InlineKeyboardMarkup(buttons)

def back_button(callback="main_menu"):
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data=callback)]])
