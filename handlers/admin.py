from aiogram import Router, types
from aiogram.filters import Command
from utils.db import save_command, delete_command, load_commands, get_command_preview

router = Router()

# Сюда впиши свой ID (можно узнать у @userinfobot)
ADMIN_ID = 7674045314


@router.message(Command("add_rp"))
async def cmd_add_rp(message: types.Message):
    """
    Добавление РП-команды с поддержкой эмодзи.

    Формат: /add_rp команда действие [эмодзи]
    Пример: /add_rp лизнуть лизнул(а) 👅
    """
    if message.from_user.id != ADMIN_ID:
        return

    parts = message.text.split(maxsplit=3)

    if len(parts) < 3:
        await message.answer(
            "⚠️ **Ошибка!** Используй:\n"
            "`/add_rp команда действие [эмодзи]`\n\n"
            "**Примеры:**\n"
            "`/add_rp лизнуть лизнул(а) 👅`\n"
            "`/add_rp обнять крепко обнял(а) 🤗`",
            parse_mode="Markdown"
        )
        return

    name = parts[1].lower()

    # Проверяем, есть ли эмодзи в конце
    if len(parts) == 4:
        # Формат: /add_rp команда действие эмодзи
        action = parts[2]
        emoji = parts[3]
    else:
        # Формат: /add_rp команда действие
        # Пробуем найти эмодзи в тексте действия
        action_parts = parts[2].split()

        # Проверяем последний символ
        if action_parts and len(action_parts[-1]) <= 2:
            # Возможно это эмодзи
            emoji = action_parts[-1]
            action = " ".join(action_parts[:-1])
        else:
            action = parts[2]
            emoji = "✨"  # Дефолтный эмодзи

    await save_command(name, action, emoji)

    # Показываем превью
    preview = get_command_preview(name, {"action": action, "emoji": emoji})

    await message.answer(
        f"✅ РП-команда успешно добавлена!\n\n"
        f"**Превью:** {preview}",
        parse_mode="Markdown"
    )


@router.message(Command("del_rp"))
async def cmd_del_rp(message: types.Message):
    """
    Удаление РП-команды.

    Формат: /del_rp команда
    """
    if message.from_user.id != ADMIN_ID:
        return

    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("⚠️ Используй: `/del_rp команда`", parse_mode="Markdown")
        return

    if await delete_command(parts[1]):
        await message.answer(f"🗑 Команда **{parts[1]}** удалена.", parse_mode="Markdown")
    else:
        await message.answer("❌ Команда не найдена.")


@router.message(Command("list_rp"))
async def cmd_list(message: types.Message):
    """
    Список всех РП-команд с превью.
    """
    if message.from_user.id != ADMIN_ID:
        return

    cmds = await load_commands()

    if not cmds:
        await message.answer("📜 Список команд пуст.")
        return

    # Формируем красивый список с превью
    text_lines = ["📜 **Список доступных РП:**\n"]

    for name, cmd_data in cmds.items():
        emoji = cmd_data.get("emoji", "✨")
        action = cmd_data.get("action", "")
        text_lines.append(f"{emoji} `{name}` → {action}")

    text = "\n".join(text_lines)
    text += f"\n\n**Всего команд:** {len(cmds)}"

    await message.answer(text, parse_mode="Markdown")


@router.message(Command("help"))
async def cmd_help(message: types.Message):
    """
    Справка по использованию бота.
    """
    help_text = """
🤖 **Справка по RP-боту**

**Для пользователей:**
• Наберите `@bot_name` в любом чате
• Начните вводить название команды (автодополнение)
• Выберите действие из списка
• Получатель может принять или отклонить

**Для админов:**
`/add_rp команда действие [эмодзи]` — добавить команду
`/del_rp команда` — удалить команду
`/list_rp` — список всех команд
`/help` — эта справка

**Примеры команд:**
• обнять 🤗
• поцеловать 💋
• ударить 👊
• погладить ✋
"""

    await message.answer(help_text, parse_mode="Markdown")