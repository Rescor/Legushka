import config
import db


async def is_trusted_chat(chat_id: int) -> bool:
    return await db.is_trusted_chat(chat_id)


def refusal_message(rest_lower: str) -> str:
    if rest_lower.startswith("кушай"):
        text = "Я не ем еду от незнакомцев."
    else:
        text = "Я так не откровенничаю в незнакомых чатах."
    return f"{text} Попроси {config.OWNER_CONTACT} добавить этот чат в доверенные."
