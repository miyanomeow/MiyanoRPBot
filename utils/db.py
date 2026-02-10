import json
import aiofiles
from functools import lru_cache
from typing import Dict, Optional
import asyncio
import os

DB_PATH = "rp_commands.json"

# Кеш для команд (будет инвалидироваться при изменениях)
_commands_cache = None
_cache_lock = asyncio.Lock()


async def load_commands() -> Dict[str, dict]:
    """
    Загружает команды из JSON файла асинхронно.

    Returns:
        Dict с командами в формате:
        {
            "команда": {
                "action": "текст действия",
                "emoji": "эмодзи"
            }
        }
    """
    global _commands_cache

    async with _cache_lock:
        # Если кеш существует, возвращаем его
        if _commands_cache is not None:
            return _commands_cache

        if not os.path.exists(DB_PATH):
            # Базовые команды при первом запуске
            default_commands = {
                "ударить": {"action": "ударил(а)", "emoji": "👊"},
                "обнять": {"action": "обнял(а)", "emoji": "🤗"},
                "поцеловать": {"action": "поцеловал(а)", "emoji": "💋"}
            }
            _commands_cache = default_commands
            return default_commands

        async with aiofiles.open(DB_PATH, "r", encoding="utf-8") as f:
            content = await f.read()
            commands = json.loads(content)

            # Поддержка старого формата (строка вместо словаря)
            normalized_commands = {}
            for name, value in commands.items():
                if isinstance(value, str):
                    # Старый формат: конвертируем в новый
                    normalized_commands[name] = {
                        "action": value,
                        "emoji": "✨"  # Дефолтный эмодзи
                    }
                else:
                    normalized_commands[name] = value

            _commands_cache = normalized_commands
            return normalized_commands


async def save_command(name: str, action: str, emoji: str = "✨") -> None:
    """
    Сохраняет РП-команду в базу данных.

    Args:
        name: Название команды (например, "обнять")
        action: Текст действия (например, "крепко обнял(а)")
        emoji: Эмодзи для команды (по умолчанию ✨)
    """
    global _commands_cache

    async with _cache_lock:
        commands = await load_commands()
        commands[name.lower()] = {
            "action": action,
            "emoji": emoji
        }

        async with aiofiles.open(DB_PATH, "w", encoding="utf-8") as f:
            await f.write(json.dumps(commands, ensure_ascii=False, indent=4))

        # Инвалидируем кеш
        _commands_cache = commands


async def delete_command(name: str) -> bool:
    """
    Удаляет команду из базы данных.

    Args:
        name: Название команды для удаления

    Returns:
        True если команда была удалена, False если не найдена
    """
    global _commands_cache

    async with _cache_lock:
        commands = await load_commands()
        if name.lower() in commands:
            del commands[name.lower()]

            async with aiofiles.open(DB_PATH, "w", encoding="utf-8") as f:
                await f.write(json.dumps(commands, ensure_ascii=False, indent=4))

            # Инвалидируем кеш
            _commands_cache = commands
            return True
        return False


def invalidate_cache() -> None:
    """Принудительная инвалидация кеша команд."""
    global _commands_cache
    _commands_cache = None


def get_command_preview(name: str, command_data: dict) -> str:
    """
    Формирует превью команды с эмодзи.

    Args:
        name: Название команды
        command_data: Данные команды (action, emoji)

    Returns:
        Строка вида "🤗 обнять → крепко обнял(а)"
    """
    emoji = command_data.get("emoji", "✨")
    action = command_data.get("action", "")
    return f"{emoji} {name} → {action}"