import random

from aiogram.types import FSInputFile, Message

import config
import db
import morphology
import state


async def handle_reaction(message: Message) -> None:
    text = message.text
    lowered = text.lower()
    from_id = message.from_user.id

    if "дай жабу" in lowered:
        await _give_sticker(message)
        return

    if lowered == "квакни":
        await message.reply_voice(FSInputFile(config.CROAK_FILE))
        return

    if "ква" in lowered:
        await message.answer("Ква!")
        return

    if await _is_reply_to_bot(message) and not await db.is_banned(from_id):
        words = text.split(" ")
        await message.answer(" ".join(morphology.froggify(w) for w in words))
        return

    await _maybe_random_reply(message)


async def _give_sticker(message: Message) -> None:
    if state.sticker_set and state.sticker_set.stickers:
        await message.reply_sticker(state.sticker_set.stickers[0].file_id)
    else:
        await message.reply("Я потеряла свою жабу ,_,")


async def _is_reply_to_bot(message: Message) -> bool:
    reply = message.reply_to_message
    return bool(reply and reply.from_user and reply.from_user.id == state.bot_user_id)


async def _maybe_random_reply(message: Message) -> None:
    roll = random.randint(0, 999)
    if roll < config.RANDOM_REPLY_CHANCE:
        await message.reply("Ква ква!")
    elif roll < config.RANDOM_REPLY_CHANCE * 2:
        await _say_random_phrase(message)


async def _say_random_phrase(message: Message) -> None:
    target = None
    for word in message.text.split():
        if morphology.morph.parse(word)[0].tag.POS == "NOUN":
            target = word
            break
    if target is None:
        return

    templates = config.QUESTIONS if random.randint(
        0, 1) == 0 else config.EXCLAMATIONS
    phrase = random.choice(templates)
    text = morphology.substitute(phrase, target)
    text = morphology.correct(text)
    await message.reply(text)
