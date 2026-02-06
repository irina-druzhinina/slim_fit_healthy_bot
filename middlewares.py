from aiogram import BaseMiddleware
from typing import Dict, Any


class UserDataMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data: Dict[str, Any]):
        from config import USERS_DATA
        user_id = str(event.from_user.id)
        data["user_data"] = USERS_DATA.setdefault(user_id, {})
        return await handler(event, data)