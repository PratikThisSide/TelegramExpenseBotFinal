from utils import progress_bar

ACHIEVEMENT_DEFS = [
    ("first_expense", "First Expense 🎉", "Log your first expense", 1, "count"),
    ("five_expenses", "Getting Started 🌟", "Log 5 expenses", 5, "count"),
    ("ten_expenses", "Expense Master ⭐", "Log 10 expenses", 10, "count"),
    ("twentyfive_expenses", "Dedicated Tracker 🏅", "Log 25 expenses", 25, "count"),
    ("fifty_expenses", "Expense Legend 👑", "Log 50 expenses", 50, "count"),
    ("hundred_expenses", "Century Club 💯", "Log 100 expenses", 100, "count"),
    ("streak_3", "3-Day Streak 🔥", "Log for 3 days in a row", 3, "streak"),
    ("streak_7", "Weekly Warrior 📅", "Log for 7 days in a row", 7, "streak"),
    ("streak_14", "Two Weeks Strong 💪", "14 day streak", 14, "streak"),
    ("streak_30", "Monthly Master 🏆", "30 day streak", 30, "streak"),
    ("budget_first", "Budget Setter 📋", "Set your first budget", 1, "budget"),
    ("under_budget_7", "Budget King 👑", "Stay under budget for 7 days", 7, "under_budget"),
    ("save_goal", "Goal Setter 🎯", "Create a savings goal", 1, "goal"),
    ("weekend_saver", "Weekend Saver 🎉", "Log expenses on a weekend", 1, "weekend"),
    ("early_bird", "Early Bird Logger 🌅", "Log before 9 AM", 1, "early"),
]

def check_achievements(db, user_id):
    count = db.get_expense_count(user_id)
    streaks = db.get_streaks(user_id)
    streak = streaks["current_streak"] if streaks else 0
    budgets = db.get_budgets(user_id)

    new_achievements = []
    for key, label, desc, threshold, atype in ACHIEVEMENT_DEFS:
        if db.unlock_achievement(user_id, key):
            if atype == "count" and count >= threshold:
                new_achievements.append((key, label, desc))
            elif atype == "streak" and streak >= threshold:
                new_achievements.append((key, label, desc))
            elif atype == "budget" and len(budgets) >= threshold:
                new_achievements.append((key, label, desc))
    return new_achievements





def get_achievements_with_status(db, user_id):
    unlocked = {row["name"] for row in db.get_achievements(user_id)}
    result = []
    for key, label, desc, threshold, atype in ACHIEVEMENT_DEFS:
        unlocked_status = key in unlocked
        result.append((key, label, desc, unlocked_status))
    return result

def get_achievement_progress(db, user_id):
    count = db.get_expense_count(user_id)
    streaks = db.get_streaks(user_id)
    streak = streaks["current_streak"] if streaks else 0
    budgets = db.get_budgets(user_id)
    progress = {}
    for key, label, desc, threshold, atype in ACHIEVEMENT_DEFS:
        if atype == "count":
            current = min(count, threshold)
            pct = (current / threshold) * 100
            progress[key] = (current, threshold, f"{progress_bar(current, threshold)} {current}/{threshold}")
        elif atype == "streak":
            current = min(streak, threshold)
            pct = (current / threshold) * 100
            progress[key] = (current, threshold, f"{progress_bar(current, threshold)} {current}/{threshold}")
    return progress
