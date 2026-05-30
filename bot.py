import os
import asyncio

from telegram import (
    Update,
    ReplyKeyboardMarkup,
)

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

from config import (
    ADMIN_ID,
    PHONE_NUMBER,
    ADDRESS,
)

from states import (
    SELECT_SESSION,
    SELECT_GUESTS,
    SELECT_TABLE,
    ENTER_NAME,
    ENTER_PHONE,
)

from keyboards import (
    main_keyboard,
    session_keyboard,
)

from database import (
    init_db,
    create_reservation,
    get_user_reservations,
    has_active_reservation,
)

from reservation import (
    get_available_tables,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "به ربات رزرو Chaplin Club خوش آمدید 🌹",
        reply_markup=main_keyboard()
    )


async def reserve_start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    user_id = update.effective_user.id

    if has_active_reservation(user_id):
        await update.message.reply_text(
            "شما یک رزرو فعال دارید.\nابتدا رزرو قبلی را لغو کنید."
        )
        return ConversationHandler.END

    await update.message.reply_text(
        "سانس موردنظر را انتخاب کنید:",
        reply_markup=session_keyboard()
    )

    return SELECT_SESSION


async def select_session(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    text = update.message.text

    if text == "سانس 1":
        context.user_data["session"] = 1

    elif text == "سانس 2":
        context.user_data["session"] = 2

    else:
        await update.message.reply_text(
            "لطفاً یکی از سانس‌ها را انتخاب کنید."
        )
        return SELECT_SESSION

    await update.message.reply_text(
        "تعداد نفرات را وارد کنید:"
    )

    return SELECT_GUESTS


async def select_guests(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    try:
        guests = int(update.message.text)
    except:
        await update.message.reply_text(
            "لطفاً فقط عدد وارد کنید."
        )
        return SELECT_GUESTS

    if guests < 1:
        await update.message.reply_text(
            "تعداد نفرات نامعتبر است."
        )
        return SELECT_GUESTS

    if guests > 4:
        await update.message.reply_text(
            f"برای رزرو بالای ۴ نفر لطفاً با {PHONE_NUMBER} تماس بگیرید."
        )
        return ConversationHandler.END

    context.user_data["guests"] = guests

    available_tables = get_available_tables(
        context.user_data["session"],
        guests
    )

    if not available_tables:
        await update.message.reply_text(
            "میز خالی برای این سانس موجود نیست."
        )
        return ConversationHandler.END

    context.user_data["available_tables"] = available_tables

    keyboard = []

    row = []

    for table_number in available_tables:
        row.append(str(table_number))

        if len(row) == 4:
            keyboard.append(row)
            row = []

    if row:
        keyboard.append(row)

    await update.message.reply_text(
        "شماره میز را انتخاب کنید:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True
        )
    )

    return SELECT_TABLE
async def select_table(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    table_text = update.message.text

    try:
        table_number = int(table_text)
    except:
        await update.message.reply_text(
            "شماره میز نامعتبر است."
        )
        return SELECT_TABLE

    if table_number not in context.user_data["available_tables"]:
        await update.message.reply_text(
            "این میز قابل انتخاب نیست."
        )
        return SELECT_TABLE

    context.user_data["table_number"] = table_number

    await update.message.reply_text(
        "نام و نام خانوادگی را وارد کنید:"
    )

    return ENTER_NAME


async def enter_name(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    context.user_data["name"] = update.message.text

    await update.message.reply_text(
        "شماره موبایل را وارد کنید:"
    )

    return ENTER_PHONE


async def enter_phone(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    phone = update.message.text

    context.user_data["phone"] = phone

    user_id = update.effective_user.id

    create_reservation(
        user_id=user_id,
        name=context.user_data["name"],
        phone=phone,
        session_number=context.user_data["session"],
        table_number=context.user_data["table_number"],
        guests=context.user_data["guests"]
    )

    await update.message.reply_text(
        f"✅ رزرو شما ثبت شد\n\n"
        f"میز: {context.user_data['table_number']}\n"
        f"سانس: {context.user_data['session']}",
        reply_markup=main_keyboard()
    )

    try:
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=
            f"📌 رزرو جدید\n\n"
            f"نام: {context.user_data['name']}\n"
            f"موبایل: {phone}\n"
            f"میز: {context.user_data['table_number']}\n"
            f"سانس: {context.user_data['session']}\n"
            f"نفرات: {context.user_data['guests']}"
        )
    except:
        pass

    return ConversationHandler.END


async def my_reservations(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    reservations = get_user_reservations(
        update.effective_user.id
    )

    if not reservations:
        await update.message.reply_text(
            "شما رزروی ندارید."
        )
        return

    text = "📋 رزروهای شما\n\n"

    for row in reservations:
        text += (
            f"شناسه: {row[0]}\n"
            f"سانس: {row[1]}\n"
            f"میز: {row[2]}\n"
            f"نفرات: {row[3]}\n\n"
        )

    await update.message.reply_text(text)


async def contact_us(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    await update.message.reply_text(
        f"📞 {PHONE_NUMBER}\n\n📍 {ADDRESS}"
    )


async def cancel_reservation(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    await update.message.reply_text(
        "در نسخه بعدی فعال می‌شود."
    )


async def main():
    init_db()

    app = Application.builder().token(
        BOT_TOKEN
    ).build()

    reservation_handler = ConversationHandler(
        entry_points=[
            MessageHandler(
                filters.Regex("^🍽 رزرو میز$"),
                reserve_start
            )
        ],
        states={
            SELECT_SESSION: [
                MessageHandler(
                    filters.TEXT,
                    select_session
                )
            ],
            SELECT_GUESTS: [
                MessageHandler(
                    filters.TEXT,
                    select_guests
                )
            ],
            SELECT_TABLE: [
                MessageHandler(
                    filters.TEXT,
                    select_table
                )
            ],
            ENTER_NAME: [
                MessageHandler(
                    filters.TEXT,
                    enter_name
                )
            ],
            ENTER_PHONE: [
                MessageHandler(
                    filters.TEXT,
                    enter_phone
                )
            ],
        },
        fallbacks=[]
    )

    app.add_handler(
        CommandHandler(
            "start",
            start
        )
    )

    app.add_handler(
        reservation_handler
    )

    app.add_handler(
        MessageHandler(
            filters.Regex("^📋 رزروهای من$"),
            my_reservations
        )
    )

    app.add_handler(
        MessageHandler(
            filters.Regex("^☎️ تماس با ما$"),
            contact_us
        )
    )

    app.add_handler(
        MessageHandler(
            filters.Regex("^❌ لغو رزرو$"),
            cancel_reservation
        )
    )

    print("Chaplin Club Bot Running...")

    await app.initialize()
    await app.start()
    await app.updater.start_polling()

    while True:
        await asyncio.sleep(3600)


if __name__ == "__main__":
    asyncio.run(main())
