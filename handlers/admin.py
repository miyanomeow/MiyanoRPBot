from aiogram import Router, types
from aiogram.filters import Command
from utils.db import save_command, delete_command, load_commands

router = Router()

# Сюда впиши свой ID (можно узнать у @userinfobot)
ADMIN_ID = 7674045314


@router.message(Command("add_rp"))
async def cmd_add_rp(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    # Формат: /add_rp кусь кусьнул(а)
    parts = message.text.split(maxsplit=2)
    if len(parts) < 3:
        await message.answer("⚠️ Ошибка! Используй: `/add_rp команда действие`\nПример: `/add_rp лизнуть лизнул(а)`")
        return

    name, action = parts[1].lower(), parts[2]
    save_command(name, action)
    await message.answer(f"✅ РП-команда *{name}* успешно добавлена/обновлена!", parse_mode="Markdown")


@router.message(Command("del_rp"))
async def cmd_del_rp(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("⚠️ Используй: `/del_rp команда`")
        return

    if delete_command(parts[1]):
        await message.answer(f"🗑 Команда *{parts[1]}* удалена.", parse_mode="Markdown")
    else:
        await message.answer("❌ Команда не найдена.")


@router.message(Command("list_rp"))
async def cmd_list(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    cmds = load_commands()
    text = "📜 **Список доступных РП:**\n" + "\n".join([f"— `{k}`: {v}" for k, v in cmds.items()])
    await message.answer(text, parse_mode="Markdown")