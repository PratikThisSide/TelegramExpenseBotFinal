<p align="center">
  <img src="banner TELE.svg" alt="Project Under Development" width="100%">
</p>

# Telegram Personal Expense Tracker Bot

A feature-rich Telegram bot for tracking personal expenses with interactive menus, charts, budgets, achievements, reminders, and more.

## Features

**Expense Tracking**
- Add expenses via natural language: `200 lunch`, `spent 500 on food`, `Coffee 150`, `Paid 450 for pizza`
- Auto-detect categories using keywords
- Undo/Edit after adding
- Search expenses by keyword or amount (`/search coffee`, `/search >500`)

**Interactive UI**
- Reply keyboard with main menu buttons
- Inline keyboards for all actions
- Expense confirmation with action buttons

**Reports & Charts**
- Pie, line, bar, and trend charts (generated with matplotlib)
- Daily, weekly, monthly, and custom date range analytics
- Auto-generated weekly (Sunday) and monthly (1st) reports

**Budget Management**
- Set per-category budgets: `/budget set food 5000`
- Visual progress bars and spending mood (🟢🟡🟠🔴)
- Alerts when budgets are exceeded

**Daily Reminder**
- Configurable daily reminder (default 9 PM): `/reminder on/off`
- User-configurable daily spending limit: `/dailylimit 500`
- Alerts if you exceed your daily limit

**Achievements & Gamification**
- 14 achievements to unlock (First Expense, 3-Day Streak, Century Club, etc.)
- XP points and level system
- Streak tracking (consecutive days)
- Progress bars for achievements

**Savings Goals & Wishlist**
- Set savings goals with progress tracking: `/goals add MacBook 120000`
- Wishlist with monthly saving estimates: `/wishlist add Laptop 70000`

**Export**
- CSV, Excel (.xlsx), and PDF export
- Styled Excel with headers and formatting

**Settings**
- Daily limit, reminder time, currency, dark mode
- All configurable via interactive menus

**Dashboard**
- `/dashboard` — see today, week, month totals, budget remaining, streak, XP, achievement progress

## Commands

```
/start                    - Main menu with buttons
/summary                  - Category breakdown this month
/total                    - Total spent this month
/list                     - Last 20 expenses
/delete <id>              - Delete an expense
/from YYYY-MM-DD to ...   - Filter by date range
/stats                    - Detailed statistics
/categories               - All categories used
/budget                   - Manage budgets
/search <query>           - Search expenses
/dashboard                - Full spending dashboard
/export                   - CSV, Excel, or PDF export
/reminder                 - Daily reminder settings
/dailylimit <amount>      - Set daily spending limit
/goals                    - Savings goals
/wishlist                 - Wishlist items
/achievements             - View unlocked badges
/fact                     - Random finance fact
/help                     - Interactive help guide
/commands                 - Show this list
/edit <id> <amt> [cat]    - Edit an expense
/reset                    - Delete all your data
```

## Setup

### Prerequisites

- Python 3.10+
- A Telegram bot token (from [@BotFather](https://t.me/BotFather))

### Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/TelegramExpenseBot.git
cd TelegramExpenseBot

# Install dependencies
pip install -r requirements.txt

# Set your bot token
export BOT_TOKEN="your_bot_token_here"

# Run the bot
python bot.py
```

### Using a config file

Edit `config.py` and set your token directly (for local development only).

## Project Structure

```
TelegramExpenseBot/
├── bot.py              # Entry point, registers handlers + scheduler
├── config.py           # Token, DB path, constants
├── database.py         # SQLite layer (8 tables, full CRUD)
├── handlers.py         # 20+ command handlers + callback router
├── keyboards.py        # Inline & reply keyboard layouts
├── utils.py            # Expense parser, date formatter, emoji maps, comparisons
├── achievements.py     # 14 achievements with XP/levels/progress
├── analytics.py        # Statistics + matplotlib charts (pie/line/bar/trend)
├── scheduler.py        # Daily reminder, weekly & monthly auto-reports
├── requirements.txt    # Python dependencies
├── render.yaml         # Render deployment config
└── start.sh            # Render start script
```

## Deployment

### Render (free)

1. Push this repo to GitHub
2. Go to [Render Dashboard](https://dashboard.render.com)
3. Click **New +** → **Blueprint**
4. Connect your GitHub repository
5. Add environment variable: `BOT_TOKEN` = your bot token
6. Click **Apply**

Render automatically uses `render.yaml` and `start.sh`. A persistent disk is mounted at `/data` so your SQLite database survives restarts.

### Fly.io

```bash
flyctl launch
flyctl secrets set BOT_TOKEN=your_token
flyctl deploy
```

## Tech Stack

- **Python 3** — Core language
- **python-telegram-bot** — Telegram Bot API framework
- **APScheduler** — Scheduled tasks (reminders, reports)
- **SQLite** — Database (single file, no server needed)
- **matplotlib** — Chart generation
- **openpyxl** — Excel export
- **fpdf2** — PDF export
