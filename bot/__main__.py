import random
import logging
from time import sleep
import traceback

from pyrogram import filters
from pyrogram import Client
from pyrogram.types import Message
from pyrogram.enums import ParseMode

from bot import app, monitored_chats, chats_map, sudo_users

logging.info("Bot Started")

@app.on_message(filters.chat(monitored_chats) & filters.incoming)
async def work(client: Client, message: Message):
    caption = None
    chat = chats_map.get(message.chat.id)

    if chat and chat.get("replace"):
        for old, new in chat["replace"].items():
            if message.media and not message.poll:
                if message.caption:
                    caption = message.caption.markdown.replace(old, new)
                else:
                    caption = None

    try:
        if message.media and not message.poll:
            for chat_id in chat["to"]:
                if caption:
                    await message.copy(chat_id, caption=caption, parse_mode=ParseMode.MARKDOWN)
                else:
                    await message.copy(chat_id)
    except Exception as e:
        logging.error(f"Error while sending message from {message.chat.id} to {chat_id}: {e}")

@app.on_message(filters.user(sudo_users) & filters.command(["fwd", "forward"]), group=1)
async def forward(client: Client, message: Message):
    if len(message.command) > 1 and message.command[1].isdigit():
        chat_id = int(message.command[1])
        if chat_id:
            try:
                offset_id = 0
                limit = 0
                if len(message.command) > 2:
                    limit = int(message.command[2])
                if len(message.command) > 3:
                    offset_id = int(message.command[3])
                async for msg in client.get_chat_history(chat_id, limit=limit, offset_id=offset_id):
                    await msg.copy(message.chat.id)
                    sleep(random.randint(1, 5))
            except Exception as e:
                await message.reply_text(f"Error:\n```{traceback.format_exc()}```")
        else:
            await message.reply_text("Invalid Chat Identifier. Give me a chat id.")
    else:
        await message.reply_text("Invalid Command\nUse /fwd {chat_id} {limit} {first_message_id}")

app.run()
