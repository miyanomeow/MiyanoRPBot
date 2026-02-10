from aiogram import Router, types
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardMarkup, \
    InlineKeyboardButton
import hashlib
from utils.db import load_commands
from utils.formatter import get_user_link

router = Router()


@router.inline_query()
async def inline_handler(inline_query: InlineQuery):
    query_text = inline_query.query.lower().strip()
    commands = load_commands()
    cmd_list = list(commands.keys())
    results = []

    user = inline_query.from_user
    initiator_link = get_user_link(user.id, user.first_name, user.username)

    for idx, name in enumerate(cmd_list):
        if query_text and name not in query_text:
            continue

        # По умолчанию для групп
        target_id = "0"
        target_text = "кого-то"

        # ПРОВЕРКА НА ЛС
        if inline_query.chat_type == "sender":
            target_text = "тебя"
            target_id = "-1"  # Метка для ЛС

        # Если в запросе указан конкретный ID (например, "обнять 12345")
        elif " " in query_text:
            parts = query_text.split()
            if len(parts) > 1 and parts[1].isdigit():
                target_id = parts[1]
                target_text = f"пользователя {target_id}"

        result_id = hashlib.md5(f"{name}:{target_id}:{idx}".encode()).hexdigest()

        # callback_data: тип:индекс:инициатор_id:цель_id
        kb = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="Принять", callback_data=f"1:{idx}:{user.id}:{target_id}"),
            InlineKeyboardButton(text="Отклонить", callback_data=f"0:{idx}:{user.id}:{target_id}")
        ]])

        results.append(
            InlineQueryResultArticle(
                id=result_id,
                title=f"{name.capitalize()} {target_text}",
                input_message_content=InputTextMessageContent(
                    message_text=f"👤 {initiator_link} хочет {name} {target_text}!",
                    parse_mode="Markdown",
                    disable_web_page_preview=True
                ),
                reply_markup=kb
            )
        )
    await inline_query.answer(results, cache_time=1)