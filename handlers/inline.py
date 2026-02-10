from aiogram import Router, types
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardMarkup, \
    InlineKeyboardButton
import hashlib
from utils.db import load_commands, get_command_preview
from utils.formatter import get_user_link

router = Router()


@router.inline_query()
async def inline_handler(inline_query: InlineQuery):
    """
    Обработчик inline-запросов с автодополнением и превью команд.

    Поддерживает:
    - Поиск по части названия команды
    - Отображение превью с эмодзи
    - Описание действия
    - Автоматическое определение цели (ЛС/группа/конкретный пользователь)
    """
    query_text = inline_query.query.lower().strip()
    commands = await load_commands()

    user = inline_query.from_user
    initiator_link = get_user_link(user.id, user.first_name, user.username)

    results = []

    # Извлекаем ID цели из запроса (если есть)
    target_id = "0"
    search_query = query_text

    if " " in query_text:
        parts = query_text.split(maxsplit=1)
        if parts[1].isdigit():
            target_id = parts[1]
            search_query = parts[0]

    # Фильтруем команды по поисковому запросу
    for idx, (name, cmd_data) in enumerate(commands.items()):
        # Автодополнение: показываем команды, которые начинаются с запроса
        # или содержат запрос в названии
        if search_query and not (name.startswith(search_query) or search_query in name):
            continue

        # Определяем текст цели
        # ЛС - это chat_type == "sender" (inline в ЛС с ботом) или "private" (обычная ЛС)
        is_private = inline_query.chat_type in ("sender", "private")

        if is_private:
            # В любых ЛС - не показываем цель вообще
            target_text = ""
            target_id = "-1"
        elif target_id != "0":
            # Указан конкретный пользователь
            target_text = f"пользователя {target_id}"
        else:
            # Общее действие в группе
            target_text = "кого-то"

        # Формируем уникальный ID для результата
        result_id = hashlib.md5(f"{name}:{target_id}:{idx}:{user.id}".encode()).hexdigest()

        # Получаем данные команды
        action = cmd_data.get("action", "")
        emoji = cmd_data.get("emoji", "✨")

        # Создаём клавиатуру с кнопками
        kb = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="✅ Принять", callback_data=f"1:{idx}:{user.id}:{target_id}"),
            InlineKeyboardButton(text="❌ Отклонить", callback_data=f"0:{idx}:{user.id}:{target_id}")
        ]])

        # Формируем превью для заголовка
        if target_text:
            title = f"{emoji} {name.capitalize()} {target_text}"
        else:
            # В ЛС - только название команды с эмодзи
            title = f"{emoji} {name.capitalize()}"

        # Описание с превью действия
        description = f"{action}"

        # Текст сообщения
        if target_text:
            message_text = f"{emoji} {initiator_link} хочет **{name}** {target_text}!"
        else:
            # В ЛС - без "кого-то" и без "использовать"
            message_text = f"{emoji} {initiator_link} хочет **{name}**!"

        results.append(
            InlineQueryResultArticle(
                id=result_id,
                title=title,
                description=description,
                input_message_content=InputTextMessageContent(
                    message_text=message_text,
                    parse_mode="Markdown",
                    disable_web_page_preview=True
                ),
                reply_markup=kb,
                # Добавляем превью в виде thumbnail (опционально)
                thumbnail_url=f"https://via.placeholder.com/100x100/667eea/ffffff?text={emoji}"
            )
        )

    # Если ничего не найдено, показываем подсказку
    if not results and search_query:
        hint_id = hashlib.md5(f"hint:{search_query}".encode()).hexdigest()
        results.append(
            InlineQueryResultArticle(
                id=hint_id,
                title="❓ Команда не найдена",
                description=f"Попробуйте другой запрос. Доступно команд: {len(commands)}",
                input_message_content=InputTextMessageContent(
                    message_text="⚠️ Команда не найдена. Используйте @bot без текста, чтобы увидеть все команды.",
                    parse_mode="Markdown"
                )
            )
        )

    # Показываем все команды, если запрос пустой
    if not search_query and not results:
        for idx, (name, cmd_data) in enumerate(commands.items()):
            emoji = cmd_data.get("emoji", "✨")
            action = cmd_data.get("action", "")

            # ЛС - это chat_type == "sender" (inline в ЛС с ботом) или "private" (обычная ЛС)
            is_private = inline_query.chat_type in ("sender", "private")

            if is_private:
                target_text = ""
                target_id = "-1"
            else:
                target_text = "кого-то"
                target_id = "0"

            result_id = hashlib.md5(f"{name}:all:{idx}".encode()).hexdigest()

            kb = InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(text="✅ Принять", callback_data=f"1:{idx}:{user.id}:{target_id}"),
                InlineKeyboardButton(text="❌ Отклонить", callback_data=f"0:{idx}:{user.id}:{target_id}")
            ]])

            results.append(
                InlineQueryResultArticle(
                    id=result_id,
                    title=f"{emoji} {name.capitalize()}" if not target_text else f"{emoji} {name.capitalize()} {target_text}",
                    description=action,
                    input_message_content=InputTextMessageContent(
                        message_text=f"{emoji} {initiator_link} хочет **{name}**!" if not target_text else f"{emoji} {initiator_link} хочет **{name}** {target_text}!",
                        parse_mode="Markdown",
                        disable_web_page_preview=True
                    ),
                    reply_markup=kb
                )
            )

    # Отправляем результаты (cache_time=1 для актуальности данных)
    await inline_query.answer(results, cache_time=1, is_personal=True)