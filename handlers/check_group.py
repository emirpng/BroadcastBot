# (c) N A C BOTS


import datetime

import config
import logging

from handlers.database import Database

DB_URL = config.DB_URL
DB_NAME = config.DB_NAME
LOG_CHANNEL = config.LOG_CHANNEL

db = Database(DB_URL, DB_NAME)

async def handle_group_status(bot, cmd):
    chat_id = cmd.chat.id
    if not await db.is_group_exist(chat_id):
        data = await bot.get_me()
        BOT_USERNAME = data.username
        await db.add_group(chat_id)
        if LOG_CHANNEL:
            await bot.send_message(
                LOG_CHANNEL,
                f"#NEWGROUP: \n\nNew Group [{cmd.from_user.first_name}](tg://group?id={cmd.from_user.id}) started @{BOT_USERNAME} !!",
            )
        else:
            logging.info(f"#NewGroup :- Name : {cmd.from_user.first_name} ID : {cmd.from_user.id}")

    ban_status = await db.get_ban_status(chat_id)
    if ban_status["is_banned"]:
        if (
            datetime.date.today() - datetime.date.fromisoformat(ban_status["banned_on"])
        ).days > ban_status["ban_duration"]:
            await db.remove_ban(chat_id)
        else:
            await cmd.reply_text("You are Banned to Use This Bot ", quote=True)
            return
    await cmd.continue_propagation()
