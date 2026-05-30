from telegram import ReplyKeyboardMarkup

MAIN_MENU = [
    ["🍽 رزرو میز"],
    ["📋 رزروهای من"],
    ["❌ لغو رزرو"],
    ["☎️ تماس با ما"],
]

SESSION_MENU = [
    ["سانس 1"],
    ["سانس 2"],
]

def main_keyboard():
    return ReplyKeyboardMarkup(
        MAIN_MENU,
        resize_keyboard=True
    )

def session_keyboard():
    return ReplyKeyboardMarkup(
        SESSION_MENU,
        resize_keyboard=True
    )
