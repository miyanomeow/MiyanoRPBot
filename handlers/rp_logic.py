from aiogram import Router, F, types
from utils.db import load_commands
from utils.formatter import get_user_link
import logging

router = Router()


@router.callback_query(F.data.regexp(r"^[01]:"))
async def handle_rp_click(callback: types.CallbackQuery):
    """
    Обработчик нажатий на кнопки "Принять/Отклонить".

    Формат callback_data: is_accepted:cmd_idx:initiator_id:target_id
    """
    try:
        data = callback.data.split(":")
        is_accepted = data[0] == "1"
        cmd_idx = int(data[1])
        initiator_id = int(data[2])
        target_id = int(data[3])

        # 1. Защита от "сам себя"
        if callback.from_user.id == initiator_id:
            return await callback.answer("❌ Нельзя взаимодействовать с собой!", show_alert=True)

        # 2. Проверка персонального действия (target_id > 0)
        if target_id > 0 and callback.from_user.id != target_id:
            return await callback.answer("⚠️ Это действие не для вас!", show_alert=True)

        # 3. Формируем ссылки
        try:
            # Пытаемся получить свежие данные инициатора
            init_chat = await callback.bot.get_chat(initiator_id)
            i_link = get_user_link(initiator_id, init_chat.first_name, init_chat.username)
        except Exception as e:
            logging.warning(f"Не удалось получить данные инициатора {initiator_id}: {e}")
            i_link = "Игрок"

        t_link = get_user_link(callback.from_user.id, callback.from_user.first_name, callback.from_user.username)

        # 4. Получаем действие из JSON
        cmds = await load_commands()
        cmd_list = list(cmds.items())

        if cmd_idx >= len(cmd_list):
            return await callback.answer("❌ Команда не найдена!", show_alert=True)

        cmd_name, cmd_data = cmd_list[cmd_idx]
        action_text = cmd_data.get("action", "")
        emoji = cmd_data.get("emoji", "✨")

        # 5. Формируем финальный текст
        if is_accepted:
            final_text = f"{emoji} {i_link} {action_text} {t_link}!"
        else:
            final_text = f"💔 {t_link} отказал(а) в действии пользователю {i_link}"

        # 6. Редактируем инлайн-сообщение
        await callback.bot.edit_message_text(
            text=final_text,
            inline_message_id=callback.inline_message_id,
            parse_mode="Markdown",
            disable_web_page_preview=True
        )

        # Уведомление пользователю
        if is_accepted:
            await callback.answer("✅ Действие принято!")
        else:
            await callback.answer("❌ Действие отклонено")

    except Exception as e:
        logging.error(f"Ошибка при обработке callback: {e}")
        await callback.answer("⚠️ Произошла ошибка", show_alert=True)