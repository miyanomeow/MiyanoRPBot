from aiogram import Router, F, types
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent
import hashlib
from utils.rp_commands import RP_ACTIONS

router = Router()


@router.inline_query()
async def inline_handler(inline_query: InlineQuery):
    text = inline_query.query.lower().strip()
    results = []

    for command, action in RP_ACTIONS.items():
        # Если пользователь что-то ввел, фильтруем команды
        if text and command not in text:
            continue

        # Генерируем уникальный ID для каждого результата
        result_id = hashlib.md5(command.encode()).hexdigest()

        # Формируем текст сообщения
        # К сожалению, Telegram Inline не знает, в кого мы "целимся",
        # поэтому обычно РП боты пишут "пользователя" или ждут упоминания в тексте.
        display_text = f"*{inline_query.from_user.first_name}* {action}"

        results.append(
            InlineQueryResultArticle(
                id=result_id,
                title=command.capitalize(),
                description=f"Выполнить действие: {command}",
                input_message_content=InputTextMessageContent(
                    message_text=display_text,
                    parse_mode="Markdown"
                )
            )
        )

    # Выводим до 50 результатов (лимит Telegram)
    await inline_query.answer(results, cache_time=1)