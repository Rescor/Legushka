from typing import Optional

from aiogram.types import StickerSet

bot_user_id: Optional[int] = None
sticker_set: Optional[StickerSet] = None
last_message_id: dict[int, int] = {}
logged_unknown_chats: set[int] = set()
