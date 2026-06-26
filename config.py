import os

TOKEN = os.getenv("BOT_TOKEN")
DB_PATH = os.getenv("DB_PATH", os.path.join(os.path.dirname(__file__), "expenses_v2.db"))
TIMEZONE = "Asia/Kolkata"
DAILY_REMINDER_DEFAULT_TIME = "21:00"
MONTHLY_REPORT_DAY = 1
WEEKLY_REPORT_DAY = "sunday"
CHART_DIR = "charts"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_ONLY_FORMAT = "%Y-%m-%d"
