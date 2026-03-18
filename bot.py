
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN_A = "!!"

# Главное меню с кнопками
def main_menu():
    keyboard = [
        [
            InlineKeyboardButton("Написать админу", callback_data="admin"),
            InlineKeyboardButton("Наш тгк", callback_data="tgk"),
        ],
        [
            InlineKeyboardButton("Тех.поддержка", callback_data="contacts"),
            InlineKeyboardButton("О нас", callback_data="mi"),
        ],
        [
            InlineKeyboardButton("Попасть в администрацию", callback_data="admins"),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def back_button():
    keyboard = [
        [InlineKeyboardButton("Назад ⬅️", callback_data="back")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "Привет!\n"
        "Тебя приветствует бот\n"
        "ⲇ𐔖ɯᥱⲇɯυύ ⲇ𐔖 ⲕ𐔖ⲏцᥲ \n"
        "Мы рады видеть тебя в нашем боте!\n\n"
        "**Главное меню**"
    )
    
    photo_path = "botpng.jpg"

    
    await update.message.reply_photo(
        photo=open(photo_path, "rb"),
        caption=text,
        parse_mode="Markdown",
        reply_markup=main_menu()
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "admin":
        await query.message.edit_text(
            "Вот подробная информация по вашему запросу.",
            reply_markup=back_button()
        )

    elif data == "admin":
        await query.message.edit_text(
            "Здесь помощь и ответы на часто задаваемые вопросы.",
            reply_markup=back_button()
        )

    elif data == "mi":
        await query.message.edit_text(
            "Свяжитесь с нами: соси@хуй",
            reply_markup=back_button()
        )

    elif data == "bot":
        await query.message.edit_text(
            "Это бот, который демонстрирует работу с inline-кнопками.",
            reply_markup=back_button()
        )

    elif data == "settings":
        await query.message.edit_text(
            "Настройки пока недоступны.",
            reply_markup=back_button()
        )

    elif data == "admins":
        await query.message.edit_text(
            "Бот A запущен! Выберите опцию:",
            reply_markup=main_menu()
        )

    else:
        await query.message.edit_text(
            "Неизвестная команда.",
            reply_markup=back_button()
        )

# Остальные команды оставляем без изменений

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "/start - Запустить бота и показать меню\n"
        "/help - Показать справку\n"
        "/info - Информация о боте\n"
        "/contact - Контактные данные\n"
        "/settings - Настройки бота"
    )
    await update.message.reply_text(help_text)

async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Этот бот демонстрирует работу с Telegram API и inline-кнопками.")

async def contact_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Связаться с нами можно по email: соси@хуй")

async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Настройки пока в разработке.")

def run_bot():
    app = ApplicationBuilder().token(TOKEN_A).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("info", info_command))
    app.add_handler(CommandHandler("contact", contact_command))
    app.add_handler(CommandHandler("settings", settings_command))

    print("Бот А стартовал")
    app.run_polling()

if __name__ == "__main__":
    run_bot()


