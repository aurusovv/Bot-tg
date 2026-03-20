
import re
import httpx
from datetime import datetime, timedelta
from telegram import ChatPermissions
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters, Application

# Множество для отслеживания пользователей, чьи сообщения нужно переслать
waiting_for_forward = set()
forwarded_messages = {}
forwarded = {}
admin_messages = {}  
admin_replies = {}

# Токен вашего бота
TOKEN = "8587360152:AAGAeoVhcFUMWHSXTuhifAH3VaujJVlhAaA"

# ID вашей группы, куда будут пересылаться сообщения
# Обязательно замените это на реальный ID вашей группы
GROUP_ID = -1003645867244
GROUP2_ID = 000
# --- Функции для создания клавиатур ---

def main_menu():
    """Создает инлайн-клавиатуру для главного меню."""
    keyboard = [
        [
            InlineKeyboardButton("Написать админу", callback_data="admin"),
            InlineKeyboardButton("Наш тгк", url="https://t.me/your_channel"),
            InlineKeyboardButton("Правила", url="https://t.me/your_channel"),
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
    """Создает инлайн-клавиатуру с кнопкой 'Назад'."""
    keyboard = [
        [InlineKeyboardButton("Назад ⬅️", callback_data="back")]
    ]
    return InlineKeyboardMarkup(keyboard)

# --- Обработчики команд ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start."""
    text = (
        "Привет!\n"
        "Тебя приветствует бот\n"
        "ⲇ𐔖ɯᥱⲇɯυύ ⲇ𐔖 ⲕ𐔖ⲏцᥲ\n"
        "Мы рады видеть тебя в нашем боте!\n\n"
        "Главное меню"
    )
    await update.message.reply_text(text, reply_markup=main_menu())

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help."""
    help_text = ("В разработке.")
    await update.message.reply_text(help_text)

async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /info."""
    await update.message.reply_text(
        "В разработке. Не доступно."
    )

async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отключает пересылку сообщений админу для пользователя."""
    user_id = update.message.chat_id
    if user_id in waiting_for_forward:
        waiting_for_forward.remove(user_id)
        await update.message.reply_text("Пересылка сообщений администрации отключена. Чтобы возобновить, снова нажмите 'Написать админу'.")
    else:
        await update.message.reply_text("Пересылка сообщений уже была отключена.")


async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /settings."""
    await update.message.reply_text("Настройки пока в разработке.")

# КОМАНДЫ ЧАТА АДМИНОВ:

def parse_time(time_str):
    """Парсит время из строки в секунды"""
    match = re.match(r"(\d+)([дdчhмmсs]?)", time_str.lower())
    if not match:
        return None
    
    amount = int(match.group(1))
    unit = match.group(2) or "д"
    
    multipliers = {"д": 86400, "d": 86400, "ч": 3600, "h": 3600, 
                   "м": 60, "m": 60, "с": 1, "s": 1}
    return amount * multipliers.get(unit, 86400)

def get_real_user_id(message):
    """Извлекает ID реального пользователя из пересланного сообщения"""
    # Проверяем, есть ли информация о пересылке
    if hasattr(message, 'forward_origin') and message.forward_origin:
        # Для новых версий python-telegram-bot
        if hasattr(message.forward_origin, 'sender_user'):
            return message.forward_origin.sender_user.id
        elif hasattr(message.forward_origin, 'chat'):
            return message.forward_origin.chat.id
    # Проверяем старый способ
    elif hasattr(message, 'forward_from') and message.forward_from:
        return message.forward_from.id
    
    # Если это сообщение от бота с текстом (запасной вариант)
    if message.from_user.is_bot and message.text:
        import re
        match = re.search(r"(\d+)", message.text)
        if match:
            return int(match.group(1))
    
    return None

async def ban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("❌ Ответьте на сообщение")
    
    # Получаем ID реального пользователя
    replied_msg = update.message.reply_to_message
    user_id = get_real_user_id(replied_msg)
    
    if not user_id:
        return await update.message.reply_text("❌ Нельзя определить пользователя (скрытый аккаунт)")
    
    chat_id = update.effective_chat.id
    
    if not context.args:
        await context.bot.ban_chat_member(chat_id, user_id)
        # Уведомляем пользователя
        try:
            await context.bot.send_message(
                user_id,
                "🚫 Вы были забанены администратором"
            )
        except:
            pass
        return await update.message.reply_text(f"✅ Пользователь забанен навсегда")
    
    seconds = parse_time(context.args[0])
    if not seconds:
        return await update.message.reply_text("❌ Пример: /ban 7д")
    
    until = datetime.now() + timedelta(seconds=seconds)
    await context.bot.ban_chat_member(chat_id, user_id, until_date=until)
    
    try:
        await context.bot.send_message(
            user_id,
            f"🚫 Вы были забанены на {context.args[0]}"
        )
    except:
        pass
    
    await update.message.reply_text(f"✅ Пользователь забанен на {context.args[0]}")

async def unban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("❌ Ответьте на сообщение")
    
    user_id = get_real_user_id(update.message.reply_to_message)
    if not user_id:
        return await update.message.reply_text("❌ Нельзя определить пользователя")
    
    await context.bot.unban_chat_member(update.effective_chat.id, user_id)
    
    try:
        await context.bot.send_message(user_id, "✅ Вы были разбанены")
    except:
        pass
    
    await update.message.reply_text("✅ Пользователь разбанен")

async def mute_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("❌ Ответьте на сообщение")
    
    # ОТЛАДКА: выводим информацию
    replied_msg = update.message.reply_to_message
    print(f"=== Отладка mute_command ===")
    print(f"ID сообщения: {replied_msg.message_id}")
    print(f"Отправитель сообщения: {replied_msg.from_user.id if replied_msg.from_user else 'None'}")
    print(f"forward_origin: {replied_msg.forward_origin}")
    
    if replied_msg.forward_origin:
        print(f"Тип forward_origin: {replied_msg.forward_origin.type}")
        if hasattr(replied_msg.forward_origin, 'sender_user'):
            print(f"sender_user: {replied_msg.forward_origin.sender_user.id if replied_msg.forward_origin.sender_user else 'None'}")
        if hasattr(replied_msg.forward_origin, 'chat'):
            print(f"chat: {replied_msg.forward_origin.chat.id if replied_msg.forward_origin.chat else 'None'}")
    
    user_id = get_real_user_id(replied_msg)
    print(f"Полученный user_id: {user_id}")
    print(f"===================")
    
    if not user_id:
        return await update.message.reply_text("❌ Нельзя определить пользователя")
    
    if not context.args:
        return await update.message.reply_text("❌ Укажите время. Пример: /mute 30м")
    
    seconds = parse_time(context.args[0])
    if not seconds:
        return await update.message.reply_text("❌ Пример: /mute 30м")
    
    until = datetime.now() + timedelta(seconds=seconds)
    
    try:
        await context.bot.restrict_chat_member(
            update.effective_chat.id,
            user_id,
            ChatPermissions(can_send_messages=False),
            until_date=until
        )
        
        try:
            await context.bot.send_message(
                user_id,
                f"🔇 Вы были замучены на {context.args[0]} и не можете писать в бот"
            )
        except:
            pass
        
        await update.message.reply_text(f"✅ Пользователь замучен на {context.args[0]}")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {e}")
        
async def unmute_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("❌ Ответьте на сообщение")
    
    user_id = get_real_user_id(update.message.reply_to_message)
    if not user_id:
        return await update.message.reply_text("❌ Нельзя определить пользователя")
    
    await context.bot.restrict_chat_member(
        update.effective_chat.id,
        user_id,
        ChatPermissions(
            can_send_messages=True,
            can_send_media_messages=True,
            can_send_polls=True,
            can_send_other_messages=True,
            can_add_web_page_previews=True
        )
    )
    
    try:
        await context.bot.send_message(user_id, "✅ Мут снят, вы снова можете писать")
    except:
        pass
    
    await update.message.reply_text("✅ Мут снят")

# --- Обработчик нажатий на инлайн-кнопки ---

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает нажатия на инлайн-кнопки."""
    query = update.callback_query
    await query.answer()  # Отвечаем на колбэк, чтобы убрать "часики" у кнопки
    data = query.data
    user_id = query.from_user.id

    if data == "admin":
        # Сохраняем ID пользователя, чтобы знать, чье сообщение пересылать
        waiting_for_forward.add(user_id)
        # Отправляем сообщение в группу, информируя администраторов о входящем сообщении
        await context.bot.send_message(GROUP_ID, f"Пользователь {query.from_user.full_name} (ID: {user_id}) хочет написать вам.")
        await query.message.edit_text("Пожалуйста, напишите ваше сообщение. Оно будет переслано администрации.", reply_markup=back_button())

    elif data == "tgk":
        await query.message.edit_text("Здесь будет ссылка на наш Telegram-канал.", reply_markup=back_button())
    elif data == "contacts":
        await query.message.edit_text("Те поддержка", reply_markup=back_button())
    elif data == "mi":
        await query.message.edit_text("Информация о нас.", reply_markup=back_button())
    elif data == "admins":
        await query.message.edit_text("Чтобы попасть в администрацию, свяжитесь с нами.", reply_markup=back_button())
    elif data == "back":
        # Возвращаемся к главному меню
        await query.message.edit_text(
            "Привет!\n"
            "Тебя приветствует бот\n"
            "ⲇ𐔖ɯᥱⲇɯυύ ⲇ𐔖 ⲕ𐔖ⲏцᥲ\n"
            "Мы рады видеть тебя в нашем боте!\n\n"
            "Главное меню",
            reply_markup=main_menu()
        )
    else:
        # Обработка неизвестных callback_data
        await query.message.edit_text("Неизвестная команда.", reply_markup=main_menu())

# --- Обработчик пересылки сообщений ---

async def forward_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Пересылает ЛЮБЫЕ сообщения от пользователя в группу админов"""
    
    if update.message.chat.type != "private":
        return
    
    if update.message.chat_id in waiting_for_forward:
        try:
            # Используем forward_message для надежной пересылки любых типов файлов
            sent = await context.bot.forward_message(
                chat_id=GROUP_ID,
                from_chat_id=update.message.chat_id,
                message_id=update.message.message_id
            )
            # Сохраняем связь для ответов
            forwarded[sent.message_id] = (update.message.from_user.id, None)
            
        except Exception as e:
            print(f"Ошибка при пересылке: {e}")
            await update.message.reply_text("❌ Ошибка при отправке. Попробуйте позже.")
    else:
        await update.message.reply_text("❌ Вы не в режиме поддержки. Используйте /start для связи с админом.")


# обработка информации сообщений от админов !!!

async def reply_to_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправляет ответ пользователю, когда админ отвечает на сообщение"""
    
    message = update.message or update.edited_message
    
    if not message or message.chat.type not in ["group", "supergroup"]:
        return
    
    # Новый ответ
    if not message.edit_date and message.reply_to_message:
        replied_msg_id = message.reply_to_message.message_id
        
        if replied_msg_id in forwarded:
            user_id, _ = forwarded[replied_msg_id]
            
            sent = await context.bot.send_message(
                chat_id=user_id,
                text=message.text
            )
            
            admin_replies[message.message_id] = (user_id, sent.message_id)
    
    # Редактирование сообщения админа
    elif message.edit_date and message.message_id in admin_replies:
        user_id, user_msg_id = admin_replies[message.message_id]
        
        try:
            await context.bot.edit_message_text(
                chat_id=user_id,
                message_id=user_msg_id,
                text=message.text
            )
        except Exception as e:
            if "Message is not modified" not in str(e):
                print(f"Ошибка при редактировании: {e}")




# --- Запуск бота ---

def run_bot():
    """Инициализирует и запускает бота."""
    # Создаем объект Application
    application = Application.builder().token(TOKEN).build()

    # команды только пользователю
    application.add_handler(CommandHandler("start", start, filters=filters.ChatType.PRIVATE))
    application.add_handler(CommandHandler("help", help_command, filters=filters.ChatType.PRIVATE))
    application.add_handler(CommandHandler("info", info_command, filters=filters.ChatType.PRIVATE))
    application.add_handler(CommandHandler("stop", stop_command, filters=filters.ChatType.PRIVATE))
    application.add_handler(CommandHandler("settings", settings_command, filters=filters.ChatType.PRIVATE))
    # Команды для группы
    application.add_handler(CommandHandler("ban", ban_command, filters=filters.ChatType.GROUPS))
    application.add_handler(CommandHandler("unban", unban_command, filters=filters.ChatType.GROUPS))
    application.add_handler(CommandHandler("mute", mute_command, filters=filters.ChatType.GROUPS))
    application.add_handler(CommandHandler("unmute", unmute_command, filters=filters.ChatType.GROUPS))


    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.ALL & filters.ChatType.PRIVATE, forward_user_message))
    application.add_handler(MessageHandler(filters.ALL & filters.ChatType.GROUPS, reply_to_user))


   

    print("Бот стартовал")
    # Запускаем бота в режиме polling
    application.run_polling()
    
if __name__ == "__main__":
    run_bot()


