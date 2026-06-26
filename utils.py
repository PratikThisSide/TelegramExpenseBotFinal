import re
import random
from datetime import datetime, date, timedelta

CATEGORY_EMOJIS = {
    "food": "🍕",
    "coffee": "☕",
    "transport": "🚕",
    "shopping": "🛒",
    "entertainment": "🎬",
    "bills": "📄",
    "health": "💊",
    "education": "📚",
    "rent": "🏠",
    "groceries": "🛍️",
    "fuel": "⛽",
    "eat out": "🍽️",
    "travel": "✈️",
    "clothing": "👕",
    "electronics": "💻",
    "gym": "🏋️",
    "subscription": "📺",
    "gift": "🎁",
    "pet": "🐾",
    "other": "📌",
}

CATEGORY_KEYWORDS = {
    "food": ["food", "lunch", "dinner", "breakfast", "snack", "meal", "eat", "restaurant", "pizza", "burger", "rice", "biryani", "curry", "paneer", "naan"],
    "coffee": ["coffee", "chai", "tea", "cafe", "latte", "espresso", "cappuccino"],
    "transport": ["uber", "ola", "auto", "cab", "taxi", "bus", "metro", "train", "transport", "fare"],
    "fuel": ["fuel", "petrol", "diesel", "gas", "refuel", "oil"],
    "shopping": ["shopping", "buy", "purchase", "amazon", "flipkart", "myntra", "mall", "store", "cloth", "dress"],
    "groceries": ["grocery", "groceries", "vegetable", "fruit", "milk", "bread", "egg", "supermarket"],
    "entertainment": ["movie", "netflix", "prime", "hotstar", "concert", "game", "ticket", "show", "cinema", "entertainment"],
    "bills": ["bill", "electricity", "water", "gas", "phone", "recharge", "internet", "wifi", "broadband"],
    "health": ["health", "doctor", "medicine", "hospital", "clinic", "pharmacy", "medical", "checkup"],
    "education": ["education", "course", "book", "class", "tuition", "fee", "school", "college", "university"],
    "rent": ["rent", "rental", "lease"],
    "travel": ["travel", "trip", "hotel", "flight", "bus ticket", "tour", "vacation"],
    "subscription": ["subscription", "spotify", "youtube", "premium", "membership"],
    "gym": ["gym", "fitness", "workout", "trainer"],
    "electronics": ["electronics", "laptop", "phone", "mobile", "charger", "cable", "battery"],
    "gift": ["gift", "present", "donation", "charity"],
    "clothing": ["clothing", "shirt", "pant", "shoe", "jacket", "jeans", "t-shirt"],
}

FUN_COMPARISONS = [
    (250, "pizzas 🍕"),
    (20, "cups of chai ☕"),
    (300, "movie tickets 🎬"),
    (200, "burger meals 🍔"),
    (100, "liters of petrol ⛽"),
    (15, "bus tickets 🚌"),
    (50, "ice creams 🍦"),
    (30, "samosa plates 🥟"),
    (500, "books 📚"),
    (10, "coffee from CCD ☕"),
]

def format_date(date_str):
    has_time = ":" in date_str
    fmt = "%Y-%m-%d %H:%M:%S" if has_time else "%Y-%m-%d"
    try:
        dt = datetime.strptime(date_str, fmt)
    except ValueError:
        return date_str
    day = dt.day
    if 4 <= day <= 20 or 24 <= day <= 30:
        suffix = "th"
    else:
        suffix = ["st", "nd", "rd"][day % 10 - 1]
    base = f"{day}{suffix} %B %Y"
    if has_time:
        base += ", %H:%M"
    return dt.strftime(base)

def format_currency(amount, currency="₹"):
    return f"{currency}{amount:,.2f}"

def get_category_emoji(category):
    cat_lower = category.lower().strip()
    for key, emoji in CATEGORY_EMOJIS.items():
        if key == cat_lower or cat_lower in key or key in cat_lower:
            return emoji
    return "📌"

def auto_detect_category(text):
    text_lower = text.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                return category.capitalize()
    return "Other"

def parse_expense(text):
    text = text.strip()
    patterns = [
        # "spent 200 on lunch" or "paid 450 for pizza"
        (r"^(?:spent|paid|used|cost)\s*(?:₹|rs\.?\s*)?(\d+\.?\d*)\s*(?:on|for|at)\s+(.+)", "num_first"),
        # "200 lunch" - number first
        (r"^(\d+\.?\d*)\s+(.+)$", "num_first"),
        # "Lunch 200" - word first
        (r"^([A-Za-z]\w*(?:\s+[A-Za-z]\w*)*)\s+(\d+\.?\d*)\s*$", "word_first"),
    ]
    for pattern, mode in patterns:
        match = re.match(pattern, text, re.IGNORECASE)
        if match:
            if mode == "num_first":
                amount = float(match.group(1))
                category = match.group(2).strip()
                category = re.sub(r"^(?:on|for|at)\s+", "", category, flags=re.IGNORECASE).strip()
            else:
                amount = float(match.group(2))
                category = match.group(1).strip()
            if category and re.match(r"^\d+\.?\d*$", category):
                continue
            if not category:
                category = auto_detect_category(text)
            return (amount, category.capitalize())
    return None

def fun_comparison(amount):
    for price, label in FUN_COMPARISONS:
        count = int(amount / price)
        if count >= 1:
            return f"That's enough for {count} {label}!"
    return None

def progress_bar(current, total, width=10):
    if total <= 0:
        return "░" * width
    filled = int((current / total) * width)
    filled = min(filled, width)
    return "█" * filled + "░" * (width - filled)

def get_month_name(offset=0):
    month = date.today().replace(day=1)
    if offset < 0:
        month = month + timedelta(days=offset * 31)
        month = month.replace(day=1)
    return month.strftime("%B %Y")

def get_date_range(period):
    today = date.today()
    if period == "today":
        return today.isoformat(), today.isoformat()
    elif period == "week":
        start = today - timedelta(days=today.weekday())
        return start.isoformat(), today.isoformat()
    elif period == "month":
        start = today.replace(day=1)
        return start.isoformat(), today.isoformat()
    elif period == "lastmonth":
        end = today.replace(day=1) - timedelta(days=1)
        start = end.replace(day=1)
        return start.isoformat(), end.isoformat()
    return today.isoformat(), today.isoformat()
