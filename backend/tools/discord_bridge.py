import asyncio
import os
import shlex
import subprocess
import sys
from typing import Optional

import discord

ONLINE_MESSAGE = "Sixx is online 🐦‍⬛"
STATUS_REPLY = "Sixx is running."
DEFAULT_SESSION_ID = "discord-dev-bridge"
OPENCLAW_TIMEOUT_SECONDS = 600


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


TOKEN = require_env("DISCORD_BOT_TOKEN")
CHANNEL_ID = int(require_env("DISCORD_CHANNEL_ID"))
SESSION_ID = os.getenv("OPENCLAW_SESSION_ID", DEFAULT_SESSION_ID)

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


async def get_target_channel() -> discord.abc.Messageable:
    channel = client.get_channel(CHANNEL_ID)
    if channel is None:
        channel = await client.fetch_channel(CHANNEL_ID)
    return channel


async def send_startup_message() -> None:
    channel = await get_target_channel()
    await channel.send(ONLINE_MESSAGE)


def run_openclaw_agent(message_text: str) -> tuple[int, str, str]:
    command = [
        "openclaw",
        "agent",
        "--message",
        message_text,
        "--deliver",
        "--reply-channel",
        "discord",
        "--reply-to",
        f"channel:{CHANNEL_ID}",
        "--session-id",
        SESSION_ID,
        "--timeout",
        str(OPENCLAW_TIMEOUT_SECONDS),
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    return result.returncode, result.stdout.strip(), result.stderr.strip()


async def relay_plain_text_command(message: discord.Message) -> None:
    async with message.channel.typing():
        code, stdout, stderr = await asyncio.to_thread(run_openclaw_agent, message.content.strip())

    if code == 0:
        return

    error_text = stderr or stdout or f"openclaw agent exited with code {code}"
    trimmed = error_text[-1500:]
    await message.reply(f"Relay failed.\n```\n{trimmed}\n```", mention_author=False)


@client.event
async def on_ready() -> None:
    print(f"Connected as {client.user}")
    try:
        await send_startup_message()
        print("Startup message sent")
    except Exception as exc:
        print(f"Failed to send startup message: {exc}", file=sys.stderr)


@client.event
async def on_message(message: discord.Message) -> None:
    if message.author == client.user:
        return

    if message.channel.id != CHANNEL_ID:
        return

    content = message.content.strip()
    if not content:
        return

    if content == "!status":
        await message.reply(STATUS_REPLY, mention_author=False)
        return

    await relay_plain_text_command(message)


if __name__ == "__main__":
    client.run(TOKEN)
