import asyncio
import json
import os
import subprocess
import sys
import uuid
from pathlib import Path

import discord

ONLINE_MESSAGE = "Sixx is online 🐦‍⬛"
STATUS_REPLY = "Sixx is running."
DEFAULT_SESSION_ID = "discord-dev-bridge"
OPENCLAW_TIMEOUT_SECONDS = 600
OPENCLAW_BIN = os.getenv("OPENCLAW_BIN", "/opt/homebrew/bin/openclaw")
STATE_PATH = Path(
    os.getenv(
        "DISCORD_BRIDGE_STATE_PATH",
        "/Users/sixx/Library/Application Support/Sixx/discord-bridge-state.json",
    )
)
DISCORD_RESPONSE_RULE = (
    "Discord response rule: return one single consolidated reply whenever reasonably possible. "
    "Avoid fragmented follow-up messages unless explicitly asked. Keep the response copy/paste friendly."
)
REHYDRATE_PROMPT = (
    "Rehydrate from the repository state only. "
    "Read repo_map.md, docs/northstar.md, docs/task_queue.md, and docs/agent_workflow.md. "
    "Summarize the current project state concisely, name the top remaining queued task, "
    "and wait for the next instruction. Ignore prior chat context unless explicitly referenced. "
    + DISCORD_RESPONSE_RULE
)


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


TOKEN = require_env("DISCORD_BOT_TOKEN")
CHANNEL_ID = int(require_env("DISCORD_CHANNEL_ID"))

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


def ensure_state_dir() -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)


def load_state() -> dict:
    ensure_state_dir()
    if not STATE_PATH.exists():
        state = {"current_session_id": DEFAULT_SESSION_ID, "previous_session_id": None}
        save_state(state)
        return state
    with STATE_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_state(state: dict) -> None:
    ensure_state_dir()
    with STATE_PATH.open("w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def get_current_session_id() -> str:
    state = load_state()
    return state.get("current_session_id", DEFAULT_SESSION_ID)


def rotate_session() -> tuple[str, str]:
    state = load_state()
    old_session = state.get("current_session_id", DEFAULT_SESSION_ID)
    new_session = f"discord-dev-{uuid.uuid4().hex[:12]}"
    state["previous_session_id"] = old_session
    state["current_session_id"] = new_session
    save_state(state)
    return old_session, new_session


async def get_target_channel() -> discord.abc.Messageable:
    channel = client.get_channel(CHANNEL_ID)
    if channel is None:
        channel = await client.fetch_channel(CHANNEL_ID)
    return channel


async def send_startup_message() -> None:
    channel = await get_target_channel()
    await channel.send(ONLINE_MESSAGE)


def run_openclaw_agent(message_text: str, session_id: str) -> tuple[int, str, str]:
    command = [
        OPENCLAW_BIN,
        "agent",
        "--message",
        message_text,
        "--session-id",
        session_id,
        "--timeout",
        str(OPENCLAW_TIMEOUT_SECONDS),
        "--json",
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    return result.returncode, result.stdout.strip(), result.stderr.strip()


async def relay_to_openclaw(message_text: str, session_id: str) -> tuple[int, str, str]:
    return await asyncio.to_thread(run_openclaw_agent, message_text, session_id)


def extract_text_from_agent_json(stdout: str) -> tuple[str, dict]:
    payload = json.loads(stdout)
    result = payload.get("result", {})
    meta = result.get("meta", {})
    parts = []
    for item in result.get("payloads", []):
        text = item.get("text")
        if text:
            parts.append(text)
    return "\n\n".join(parts).strip(), meta


async def relay_plain_text_command(message: discord.Message) -> None:
    session_id = get_current_session_id()
    effective_message = f"{DISCORD_RESPONSE_RULE}\n\nUser request:\n{message.content.strip()}"
    async with message.channel.typing():
        code, stdout, stderr = await relay_to_openclaw(effective_message, session_id)

    if code != 0:
        error_text = stderr or stdout or f"openclaw agent exited with code {code}"
        trimmed = error_text[-1500:]
        await message.reply(f"Relay failed.\n```\n{trimmed}\n```", mention_author=False)
        return

    try:
        text, _meta = extract_text_from_agent_json(stdout)
    except Exception as exc:
        trimmed = stdout[-1500:]
        await message.reply(f"Relay parse failed: {exc}\n```\n{trimmed}\n```", mention_author=False)
        return

    if not text:
        text = "(No text response returned.)"

    await message.reply(text, mention_author=False)


async def handle_status(message: discord.Message) -> None:
    current_session = get_current_session_id()
    await message.reply(
        f"{STATUS_REPLY}\nCurrent Discord work session: `{current_session}`",
        mention_author=False,
    )


async def handle_new_session(message: discord.Message) -> None:
    old_session, new_session = rotate_session()
    await message.reply(
        (
            f"Started new Discord work session: `{new_session}`\n"
            f"Retired previous session from routing: `{old_session}`"
        ),
        mention_author=False,
    )


async def handle_show_session(message: discord.Message) -> None:
    current_session = get_current_session_id()
    await message.reply(f"Current Discord work session: `{current_session}`", mention_author=False)


async def handle_rehydrate(message: discord.Message) -> None:
    session_id = get_current_session_id()
    async with message.channel.typing():
        code, stdout, stderr = await relay_to_openclaw(REHYDRATE_PROMPT, session_id)

    if code != 0:
        error_text = stderr or stdout or f"openclaw agent exited with code {code}"
        trimmed = error_text[-1500:]
        await message.reply(f"Rehydrate failed.\n```\n{trimmed}\n```", mention_author=False)
        return

    try:
        text, _meta = extract_text_from_agent_json(stdout)
    except Exception as exc:
        trimmed = stdout[-1500:]
        await message.reply(f"Rehydrate parse failed: {exc}\n```\n{trimmed}\n```", mention_author=False)
        return

    await message.reply(text or "Rehydrate complete.", mention_author=False)


@client.event
async def on_ready() -> None:
    print(f"Connected as {client.user}")
    try:
        load_state()
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
        await handle_status(message)
        return

    if content == "!new-session":
        await handle_new_session(message)
        return

    if content == "!session":
        await handle_show_session(message)
        return

    if content == "!rehydrate":
        await handle_rehydrate(message)
        return

    await relay_plain_text_command(message)


if __name__ == "__main__":
    client.run(TOKEN)
