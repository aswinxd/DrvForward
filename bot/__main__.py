import random
import logging
from time import sleep
import traceback

from pyrogram import filters

from bot import app, monitored_chats, chats_map, sudo_users
from pyrogram.types import Message
from pyrogram.enums import ParseMode
from pyrogram import Client

logging.info("Bot Started")

@app.on_message(filters.chat(monitored_chats) & filters.incoming)
def work(_: Client, message: Message):
    caption = None
    chat = chats_map.get(message.chat.id)

    if chat.get("replace"):
        for old, new in chat["replace"].items():
            if message.media and not message.poll:
                caption = message.caption.markdown.replace(old, new)
                
    try:
        if message.media and not message.poll:
            for chat_id in chat["to"]:
                if caption:
                    message.copy(chat_id, caption=caption, parse_mode=ParseMode.MARKDOWN)
                else:
                await message.copy(chat_id)
    except Exception as e:
        logging.error(f"Error while sending message from {message.chat.id} to {chat_id}: {e}")


@app.on_message(filters.user(sudo_users) & filters.command(["fwd", "forward"]), group=1)
def forward(client: Client, message: Message):
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
                for msg in client.get_chat_history(chat_id, limit=limit, offset_id=offset_id):
                    msg.copy(message.chat.id)
                    sleep(random.randint(1, 5))
            except Exception as e:
                message.reply_text(f"Error:\n```{traceback.format_exc()}```")
        else:
            message.reply_text("Invalid Chat Identifier. Give me a chat id.")
    else:
        message.reply_text("Invalid Command\nUse /fwd {chat_id} {limit} {first_message_id}")
        
app.run()
