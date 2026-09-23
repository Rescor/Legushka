import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

BOT_TOKEN = os.environ["BOT_TOKEN"]

_initial_friend = os.environ.get("INITIAL_FRIEND_ID", "").strip()
INITIAL_FRIEND_ID = int(_initial_friend) if _initial_friend else None

OWNER_CONTACT = os.environ.get("OWNER_CONTACT", "моему владельцу")

LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()

DB_PATH = BASE_DIR / "data" / "legushka.db"
CROAK_FILE = BASE_DIR / "assets" / "croak.ogg"

STICKER_SET_NAME = os.environ.get("STICKER_SET_NAME", "Busyastickerset")

# Имена, на которые отзывается Буся. Задать свои можно через запятую в .env.
NAME_ALIASES = [
    name.strip()
    for name in os.environ.get("NAME_ALIASES", "буся,легушька").split(",")
    if name.strip()
]

RANDOM_REPLY_CHANCE = 3  # шанс случайной реакции на сообщение, x/1000

# На сколько сообщений "отредактированное" должно отставать от самого
# последнего в чате, чтобы считаться старым и вызвать
# предупреждение о редактировании.
EDIT_STALENESS_THRESHOLD = 10
EDIT_WARNING_ENABLED = os.environ.get(
    "EDIT_WARNING_ENABLED", "false").strip().lower() == "true"

LETTERS = (
    "бвгджзйклмнпрстфхцшщчъьБВГДЖЗЙКЛМНПРСТФХЦЧШЩЪЬаеёиоуыэюяАЕЁИОУЫЭЮЯ"
    "bcdfghjklmnpqrstvwxzBCDFGHJKLMNPQRSTVWXZaeiouyAEIOUY"
)
ENG_LETTERS = "bcdfghjklmnpqrstvwxzBCDFGHJKLMNPQRSTVWXZaeiouyAEIOUY"
VOWELS = "аеёиоуыэюяАЕЁИОУЫЭЮЯaeiouyAEIOUY"
MARKS = "!?.,:;"

# Шаблоны случайных фраз. Собираются в morphology.substitute() вокруг
# подлежащего - существительного, которое Буся выцепила из чужого сообщения
# (subject_word). Каждый элемент списка-шаблона - это либо кусок текста
# (вставляется как есть), либо один из двух маркеров:
#   0, {падежи}            - подставить само подлежащее в этой форме
#   1, {падежи}, "слово"   - подставить "слово" (например, местоимение) в
#                            этой форме, согласованное с родом/числом
#                            подлежащего
#
# Пример: ["Что такое", 0, {"nomn"}, "?"] при подлежащем "жаба" даёт
# "Что такое жаба?" (0 = подставить "жаба" в именительном падеже).
#
# ["Поквакаем об", 1, {"loct"}, "этот", 0, {"loct"}, "?"] при подлежащем
# "болото" даёт "Поквакаем об этом болоте?" ("этот" согласуется с родом
# "болота" (ср. род) и ставится в предложный падеж => "этом", затем само
# "болото" - тоже в предложный падеж => "болоте").
QUESTIONS = [
    ["Что такое", 0, {"nomn"}, "?"],
    ["Как понять", "-", 0, {"nomn"}, "?"],
    ["Зачем жабам", 0, {"nomn"}, "?"],
    ["Ква ква, ква - ", 0, {"accs"}, "ква ква ква?"],
    ["Поквакаем об", 1, {"loct"}, "этот", 0, {"loct"}, "?"],
]

EXCLAMATIONS = [
    ["А мне", 1, {"pres", "3per"}, "нравиться", 0, {"nomn"}, "!"],
    ["А я знаю тайну об", 1, {"loct"}, "этот", 0, {"loct"}, "..."],
    ["Вы знали, что лягушки любят", 0, {"accs"}, "?"],
    ["Когда я была головастиком, я боялась", 0,
        {"accs", "plur"}, ". Не знаю, почему!"],
    ["Зачем тебе эти", 0, {"nomn", "plur"}, "? Скука полная!"],
    ["У нас в болоте говорят, что", 0, {"nomn", "plur"}, "- опасная штука!"],
]

_NAMES_LIST = ", ".join(alias.capitalize() for alias in NAME_ALIASES)
_PRIMARY = NAME_ALIASES[0].capitalize()

GREETINGS = (
    "Привет! Я жабка Буся. Я не общаюсь в личных сообщениях, только в беседах. Я знаю команды:"
    f"\n• <code>{_PRIMARY}, кто я</code> — узнать отношение меня к тебе"
    f"\n• <code>{_PRIMARY}, сколько весишь</code> — узнать мой вес"
    f"\n• <code>{_PRIMARY}, кушай &lt;еда&gt;</code> — покормить меня едой"
    f"\n• <code>{_PRIMARY}, что ты ешь</code> — узнать, что я ем чаще всего"
    f"\n• <code>{_PRIMARY}, любимая еда</code> — узнать, какая еда мне нравится больше всего"
    "\n• <code>Дай жабу</code> — даю тебе жабу бесплатно без смс и регистрации"
    "\n• <code>Квакни</code> — квакаю"
    "\n• <code>Ква</code> — ква ква ква?"
    f"\n\nОбращаться ко мне можно по любому из этих имён: {_NAMES_LIST}."
    "\nТакже у меня есть скрытые функции, которые можно узнать, только если достаточно долго"
    " за мной наблюдать. Ква! 🐸"
)
