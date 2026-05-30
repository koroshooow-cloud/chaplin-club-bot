import os
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")

ADMIN_ID = 5088510875

MAIN_MENU = [
    ["🍽 رزرو میز"],
    ["📋 رزروهای من"],
    ["❌ لغو رزرو"],
    ["☎️ تماس با ما"]
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = ReplyKeyboardMarkup(
        MAIN_MENU,
        resize_keyboard=True
    )

    await update.message.reply_text(
        "به ربات رزرو Chaplin Club خوش آمدید 🌹",
        reply_markup=keyboard
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "☎️ تماس با ما":
        await update.message.reply_text(
            "📞 09030000440\n\n📍 کیش، دیپلمات تجاری، رستوران چاپلین"
        )

    elif text == "🍽 رزرو میز":
        await update.message.reply_text(
            "سیستم رزرو در مرحله بعدی فعال خواهد شد."
        )

    elif text == "📋 رزروهای من":
        await update.message.reply_text(
            "فعلاً رزروی ثبت نشده است."
        )

    elif text == "❌ لغو رزرو":
        await update.message.reply_text(
            "فعلاً رزروی برای لغو وجود ندارد."
        )

async def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Chaplin Club Bot Running...")
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
