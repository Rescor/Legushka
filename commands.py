import random
from typing import Optional

import psutil
from aiogram.types import Message

import chat_access
import config
import db
import morphology

_process = psutil.Process()


def _strip_alias(text: str) -> Optional[str]:
    lowered = text.lower()
    for alias in config.NAME_ALIASES:
        prefix = f"{alias.lower()}, "
        if lowered.startswith(prefix):
            return text[len(prefix):]
    return None


def _is_male(user_id: int) -> bool:
    # Пол определяется по чётности Telegram ID.
    return user_id % 2 == 1


def _reply_target(message: Message) -> Optional[int]:
    reply = message.reply_to_message
    if reply and reply.from_user:
        return reply.from_user.id
    return None


async def _is_chat_admin(message: Message, user_id: int) -> bool:
    member = await message.bot.get_chat_member(message.chat.id, user_id)
    return member.status in ("creator", "administrator")


async def _set_chat_trust(
    message: Message, from_id: int, rest: str, keyword: str, trust: bool
) -> None:
    if from_id != config.INITIAL_FRIEND_ID:
        return

    arg = rest[len(keyword):].strip()
    if not arg or arg.lower() == "чату":
        # Без id - доверяем/перестаём доверять чату, в котором это написали.
        # Так владелец может закинуть Бусю в новый чат и сразу же там
        # написать "буся, доверяй", не выясняя id чата отдельно.
        chat_id = message.chat.id
    else:
        try:
            chat_id = int(arg)
        except ValueError:
            await message.reply("Квак? Это не похоже на id чата.")
            return

    already_trusted = await db.is_trusted_chat(chat_id)
    if trust:
        if already_trusted:
            await message.reply(f"Я уже доверяю чату {chat_id}.")
        else:
            await db.add_trusted_chat(chat_id)
            await message.reply(f"Буду доверять чату {chat_id}.")
    else:
        if not already_trusted:
            await message.reply(f"Я и так не доверяю чату {chat_id}.")
        else:
            await db.remove_trusted_chat(chat_id)
            await message.reply(f"Перестаю доверять чату {chat_id}.")


async def handle_command(message: Message) -> bool:
    rest = _strip_alias(message.text)
    if rest is None:
        return False

    rest_lower = rest.lower()
    from_id = message.from_user.id

    if rest_lower.startswith("не доверяй"):
        await _set_chat_trust(message, from_id, rest, "не доверяй", trust=False)
        return True

    if rest_lower.startswith("доверяй"):
        await _set_chat_trust(message, from_id, rest, "доверяй", trust=True)
        return True

    if rest_lower.startswith("выплюнь"):
        await _spit_out(message, from_id, rest[len("выплюнь"):].strip())
        return True

    if not await chat_access.is_trusted_chat(message.chat.id):
        await message.reply(chat_access.refusal_message(rest_lower))
        return True

    if rest_lower.startswith("память"):
        if await db.is_trusted(from_id):
            mb = _process.memory_info().rss / 1024 ** 2
            await message.reply(f"Я занимаю {mb:.1f} МБ памяти.")
        return True

    if rest_lower.startswith("кто я"):
        if await db.is_trusted(from_id):
            await message.reply("Ты " + ("друг!" if _is_male(from_id) else "подруга!"))
        elif await db.is_banned(from_id):
            await message.reply("Ты меня " + ("обижал!" if _is_male(from_id) else "обижала!"))
        else:
            await message.reply("Ты мо" + ("й знакомый!" if _is_male(from_id) else "я знакомая!"))
        return True

    if rest_lower.startswith("фас"):
        if await db.is_trusted(from_id):
            target = _reply_target(message)
            if target is not None:
                await message.reply(f"Квак: {target}")
            else:
                await message.reply("Квак.")
        return True

    if rest_lower.startswith("бан"):
        if await db.is_trusted(from_id):
            target = _reply_target(message)
            if target is not None and target == config.INITIAL_FRIEND_ID:
                await message.reply("Квак! Эту жабу нельзя обидеть.")
            elif target is not None:
                if await db.is_trusted(target):
                    await db.remove_trusted(target)
                    await message.reply("Я не буду дружить с этим человеком.")
                else:
                    await db.add_banned(target)
                    await message.reply("Я буду игнорировать этого человека.")
            else:
                await message.reply("Квак.")
        return True

    if rest_lower.startswith("дружи"):
        if await db.is_trusted(from_id):
            target = _reply_target(message)
            if target is not None:
                if await db.is_banned(target):
                    await db.remove_banned(target)
                    await message.reply("Я не буду игнорировать этого человека.")
                else:
                    await db.add_trusted(target)
                    await message.reply("Буду дружить!")
            else:
                await message.reply("Квак.")
        return True

    if rest_lower.startswith("хватит реагировать на изменение сообщений"):
        if await _is_chat_admin(message, from_id):
            if not await db.is_edit_ignored(message.chat.id):
                await db.set_edit_ignored(message.chat.id, True)
                await message.reply(
                    "Я больше не буду реагировать на изменения сообщений в этом чате."
                )
            else:
                await message.reply("Я уже не реагирую на изменения сообщений в этом чате!")
        else:
            await message.reply("Пусть меня попросит об этом админ чата.")
        return True

    if rest_lower.startswith("реагируй на изменение сообщений"):
        if await _is_chat_admin(message, from_id):
            if await db.is_edit_ignored(message.chat.id):
                await db.set_edit_ignored(message.chat.id, False)
                await message.reply("Теперь я буду реагировать на изменения сообщений в этом чате.")
            else:
                await message.reply("Я и так реагирую на изменения сообщений в этом чате!")
        else:
            await message.reply("Пусть меня попросит об этом админ чата.")
        return True

    if rest_lower.startswith("сколько ты весишь"):
        size = await db.get_size()
        weight = (size / 100) ** 2 * 96.8024
        await message.reply(f"<b>Я вешу {weight:.1f} кг.</b>")
        return True

    if rest_lower.startswith("любимая еда"):
        top = await db.top_treats_by_nutrition(10)
        if top:
            entries = [f"{name} {nutrition:.2f}" for name, nutrition in top]
            await message.reply("Моя любимая еда:\n" + "\n".join(entries))
        else:
            await message.reply("Меня еще ничем не кормили!")
        return True

    if rest_lower.startswith("кушай"):
        await _feed(message, rest[len("кушай"):].strip())
        return True

    if rest_lower.startswith("что ты ешь"):
        top = await db.top_treats_by_times_eaten(10)
        if not top:
            await message.reply("Меня еще ничем не кормили!")
        else:
            lines = []
            for name, times in top:
                form = morphology.morph.parse(
                    name)[0].inflect({"sing", "accs"})
                word = form.word if form else name
                lines.append(f"{word} - {times} раз")
            await message.reply("Я чаще всего ем:\n" + "\n".join(lines))
        return True

    return False


async def _feed(message: Message, treat: str) -> None:
    if len(treat) > 20:
        await message.reply("Хватит баловаться!")
        return
    if not treat or not all(ch in config.LETTERS for ch in treat):
        await message.reply("Я не поняла, что мне надо есть?")
        return

    normal = morphology.morph.parse(treat)[0].normal_form
    existing = await db.get_treat(normal)
    if existing:
        nutrition, _times = existing
    else:
        nutrition = random.gauss(0.95, 0.4)
        if nutrition > 1.9:
            nutrition = random.uniform(2.0, 10.0)
    await db.feed_treat(normal, nutrition)

    size = await db.get_size() + nutrition
    await db.set_size(size)
    await message.reply(f"<b>Буся выросла до {size:.1f} см.</b>")


async def _spit_out(message: Message, from_id: int, treat: str) -> None:
    if from_id != config.INITIAL_FRIEND_ID:
        return
    if not treat:
        await message.reply("Квак? Что выплюнуть?")
        return

    normal = morphology.morph.parse(treat)[0].normal_form
    if not await db.get_treat(normal):
        await message.reply(f"Я и не ела {normal}.")
        return

    await db.delete_treat(normal)
    await message.reply(f"Квак, больше не буду есть {normal}.")
