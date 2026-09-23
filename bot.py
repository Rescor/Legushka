import asyncio
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Message

import chat_access
import commands
import config
import db
import edited
import reactions
import state

logging.basicConfig(
    level=config.LOG_LEVEL,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("legushka")


async def on_private_message(message: Message) -> None:
    await message.reply(config.GREETINGS)


async def on_group_message(message: Message) -> None:
    if message.from_user is None:
        return

    state.last_message_id[message.chat.id] = message.message_id

    if (
        message.chat.id not in state.logged_unknown_chats
        and not await chat_access.is_trusted_chat(message.chat.id)
    ):
        state.logged_unknown_chats.add(message.chat.id)
        logger.info(
            "Сообщение из недоверенного чата %r (id=%s) - напиши там"
            " \"<имя>, доверяй\", если он должен быть доверенным",
            message.chat.title or message.chat.id,
            message.chat.id,
        )

    try:
        handled = await commands.handle_command(message)
        if not handled:
            await reactions.handle_reaction(message)
    except Exception:
        logger.exception(
            "Не удалось обработать сообщение в чате %s", message.chat.id)


async def on_edited_message(message: Message) -> None:
    if message.from_user is None:
        return

    try:
        await edited.handle_edited(message)
    except Exception:
        logger.exception(
            "Не удалось обработать редактирование сообщения в чате %s", message.chat.id)


async def main() -> None:
    bot = Bot(
        token=config.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    await db.init()

    if config.INITIAL_FRIEND_ID is not None:
        await db.add_trusted(config.INITIAL_FRIEND_ID)
        logger.info("INITIAL_FRIEND_ID %s добавлен в список друзей",
                    config.INITIAL_FRIEND_ID)

    me = await bot.get_me()
    state.bot_user_id = me.id
    logger.info("Вошла как @%s (id=%s)", me.username, me.id)

    try:
        state.sticker_set = await bot.get_sticker_set(config.STICKER_SET_NAME)
        logger.info(
            "Стикерпак %s загружен",
            config.STICKER_SET_NAME,
        )
    except Exception:
        logger.exception(
            "Не удалось загрузить стикерпак %s - 'дай жабу' будет недоступна до перезапуска",
            config.STICKER_SET_NAME,
        )

    dp = Dispatcher()
    dp.message.register(on_private_message, F.chat.type == "private")
    dp.message.register(on_group_message, F.chat.type != "private", F.text)
    if config.EDIT_WARNING_ENABLED:
        dp.edited_message.register(on_edited_message, F.chat.type != "private")

    try:
        await dp.start_polling(bot)
    finally:
        await db.close()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
