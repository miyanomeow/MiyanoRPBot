def get_user_link(user_id: int, first_name: str, username: str = None) -> str:
    """Формирует Markdown ссылку на пользователя без пинга."""
    if username:
        return f"[{first_name}](https://t.me/{username})"
    return f"[{first_name}](tg://user?id={user_id})"