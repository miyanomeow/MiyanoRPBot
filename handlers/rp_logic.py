from aiogram import Router, F, types
from utils.db import load_commands
from utils.formatter import get_user_link

router = Router()

@router.callback_query(F.data.regexp(r"^[01]:"))
async def handle_rp_click(callback: types.CallbackQuery):
    data = callback.data.split(":")
    is_accepted = data[0] == "1"
    cmd_idx = int(data[1])
    initiator_id = int(data[2])
    target_id = int(data[3])

    # 1. Защита от "сам себя"
    if callback.from_user.id == initiator_id:
        return await callback.answer("Нельзя взаимодействовать с собой!", show_alert=True)

    # 2. Проверка персонального действия (target_id > 0)
    if target_id > 0 and callback.from_user.id != target_id:
        return await callback.answer("Это действие не для вас!", show_alert=True)

    # 3. Формируем ссылки
    try:
        # Пытаемся получить свежие данные инициатора
        init_chat = await callback.bot.get_chat(initiator_id)
        i_link = get_user_link(initiator_id, init_chat.first_name, init_chat.username)
    except:
        i_link = "Игрок"

    t_link = get_user_link(callback.from_user.id, callback.from_user.first_name, callback.from_user.username)

    # 4. Получаем действие из JSON
    cmds = load_commands()
    cmd_name = list(cmds.keys())[cmd_idx]
    action_text = cmds[cmd_name]

    if is_accepted:
        final_text = f"{i_link} {action_text} {t_link}!"
    else:
        final_text = f"{t_link} отказал(а) в действии пользователю {i_link} 💔"

    # 5. Редактируем инлайн-сообщение
    await callback.bot.edit_message_text(
        text=final_text,
        inline_message_id=callback.inline_message_id,
        parse_mode="Markdown",
        disable_web_page_preview=True
    )
    await callback.answer()