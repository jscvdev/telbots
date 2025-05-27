import asyncio
import re
from telethon import TelegramClient, events

# --- Config ---
API_ID = 28691550
API_HASH = "a5d0a2626b193aad2e33a87ce99b935d"
SESSION_NAME = "auto_clicker"
OPGMBOT_USERNAME = "opgmbot"
DEBUG = True  # Set to True to enable logging

client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

# --- Regex patterns ---
UUID_PATTERN = re.compile(
    r"\b[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}\b"
)
ALPHANUM_PATTERN = re.compile(
    r"\b[A-Za-z0-9]{3}\s[A-Za-z0-9]{3}\s\d{2}\s\d{2}\s\d{2}\b"
)

sent_codes = set()

async def fast_click(message):
    try:
        if not message.buttons:
            return
        for row in message.buttons:
            for button in row:
                if button and button.text and 'get' in button.text.lower():
                    if button.data:
                        await message.click(data=button.data)
                    else:
                        await message.click(text=button.text.strip())
                    if DEBUG:
                        print(f"[✅ Clicked] '{button.text.strip()}'")
                    return
    except Exception as e:
        if DEBUG:
            print(f"[❌ Click Error] {e}")

def is_from_opgmbot(message):
    return (
        (message.via_bot and message.via_bot.username == OPGMBOT_USERNAME)
        or (message.fwd_from and getattr(message.fwd_from.from_id, 'user_id', None))
    )

async def process_message(message):
    raw = message.raw_text
    if not raw:
        return

    if is_from_opgmbot(message):
        asyncio.create_task(fast_click(message))

    matches = UUID_PATTERN.findall(raw) + ALPHANUM_PATTERN.findall(raw)
    if DEBUG and matches:
        print(f"[🔍 Detected] Matches: {matches}")

    for code in matches:
        code = code.strip()
        if code not in sent_codes:
            try:
                await client.send_message(OPGMBOT_USERNAME, code)
                sent_codes.add(code)
                if DEBUG:
                    print(f"[📤 Sent to @opgmbot] Code: {code}")
            except Exception as e:
                if DEBUG:
                    print(f"[❌ Send Error] {e}")

@client.on(events.NewMessage(func=lambda e: e.message.raw_text or e.message.reply_markup))
async def on_new_message(event):
    await process_message(event.message)

@client.on(events.MessageEdited(func=lambda e: e.message.raw_text or e.message.reply_markup))
async def on_message_edit(event):
    await process_message(event.message)

async def main():
    await client.start()
    print("🚀 Bot started.")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
