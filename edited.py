from aiogram.types import Message

import config
import db
import state


async def handle_edited(message: Message) -> None:
    if await db.is_edit_ignored(message.chat.id):
        return

    latest = state.last_message_id.get(message.chat.id, 0)
    if latest - message.message_id > config.EDIT_STALENESS_THRESHOLD:
        await message.reply(
            "<b>ВНИМАНИЕ!</b> Вот это сообщение было отредактировано только что."
        )
