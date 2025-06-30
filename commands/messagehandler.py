import discord
import dotenv
import os
import random
from discord import Message, Guild
from discord.ext.commands import Bot
from discord.utils import get
from pathlib import Path

dotenv.load_dotenv()
CURSE_WORDS = tuple(map(str.lower, os.getenv("CURSE_WORDS").split(", ")))
PRESIDENT = os.getenv("PRESIDENT_USERNAME")
PRESIDENT_TITLE = os.getenv("PRESIDENT_TITLE")
BOT_LOG_CHANNEL = int(os.getenv("BOT_LOG_CHANNEL"))
BASE_PATH = Path(os.getenv("BASE_PATH"))
UWU_IMAGE_PATH = str((BASE_PATH / "uwu.png").resolve())


async def message_handler(message: Message, server: Guild, client: Bot):
    profanity_detected = await profanity_handler(message, server)
    if not profanity_detected:
        await uwu_handler(message)
    await client.process_commands(message)


async def profanity_handler(message: Message, server: Guild) -> bool:
    "Responds to messages with profanity, or does nothing if no profanity. Returns whether profanity was detected in message"
    if profanity_permitted(message):
        return False
    profanity = detect_profanity(message)
    if not profanity:
        return False

    audit_embed = discord.Embed(
        title="Swear detected",
        description=str(message.author),
        color=0xFC3232,
        timestamp=message.created_at,
    )
    audit_embed.add_field(
        name="Original Message", value=message.content, inline=False
    )
    audit_embed.add_field(name="Offending Word(s)",
                          value=", ".join(profanity), inline=False)
    audit_embed.add_field(
        name="Channel", value=message.channel.name, inline=False
    )
    await get(server.channels, id=BOT_LOG_CHANNEL).send(embed=audit_embed)
    return True


def profanity_permitted(message: Message) -> bool:
    return message.channel.is_nsfw() or message.author.bot


def detect_profanity(message: Message) -> tuple[str, ...]:
    return tuple(curse_word for curse_word in CURSE_WORDS if curse_word in message.content.lower())


async def profanity_response(message: Message):
    response = "Hey, please check your message for swears!"
    if str(message.author) == PRESIDENT:
        response = f"Hey, please check your mess-Oh, I'm sorry {PRESIDENT_TITLE}. President, I didn't realize it was you! I'll look the other way this time but please watch your language in the future!"
    await message.channel.send(response)


async def uwu_handler(message: Message):
    if message.author.bot:
        return
    uwu_map = {
        "uwu": "owo",
        "owo": "uwu",
        "uwo": "owu",
        "owu": "uwo",
    }
    first_match = next((power_word for power_word in uwu_map.keys(
    ) if power_word in message.content.lower()), None)
    if first_match == "uwu" and random.randint(1, 10) == 1:
        await message.channel.send(file=discord.File(UWU_IMAGE_PATH))
    elif first_match is not None:
        await message.channel.send(uwu_map[first_match])
