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
