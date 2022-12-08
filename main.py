import os
import traceback
import logging

from pyrogram import Client
from pyrogram import StopPropagation, filters
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

import config
from handlers.broadcast import broadcast
from handlers.check_group import handle_group_status
from handlers.database import Database

LOG_CHANNEL = config.LOG_CHANNEL
AUTH_USERS = config.AUTH_USERS
DB_URL = config.DB_URL
DB_NAME = config.DB_NAME

db = Database(DB_URL, DB_NAME)


Bot = Client(
    "BroadcastBot",
    bot_token=config.BOT_TOKEN,
    api_id=config.API_ID,
    api_hash=config.API_HASH,
)

@Bot.on_message(filters.group)
async def _(bot, cmd):
    await handle_group_status(bot, cmd)

@Bot.on_message(filters.command("start") & filters.group)
async def startgroup(client, message):
    # return
    chat_id = message.chat.id
    if not await db.is_group_exist(chat_id):
        data = await client.get_me()
        BOT_USERNAME = data.username
        await db.add_group(chat_id)
        if LOG_CHANNEL:
            await client.send_message(
                LOG_CHANNEL,
                f"#NEWGROUP: \n\nNew Group [{message.from_group.first_name}](tg://group?id={message.from_group.id}) started @{BOT_USERNAME} !!",
            )
        else:
            logging.info(f"#NewGroup :- Name : {message.from_group.first_name} ID : {message.from_group.id}")
    joinButton = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("CHANNEL", url="https://t.me/nacbots"),
                InlineKeyboardButton(
                    "SUPPORT GROUP", url="https://t.me/n_a_c_bot_developers"
                ),
            ]
        ]
    )
    raise StopPropagation


@Bot.on_message(filters.command("settings"))
async def opensettings(bot, cmd):
    group_id = cmd.from_group.id
    await cmd.reply_text(
        f"`Here You Can Set Your Settings:`\n\nSuccessfully setted notifications to **{await db.get_notif(group_id)}**",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        f"NOTIFICATION  {'🔔' if ((await db.get_notif(group_id)) is True) else '🔕'}",
                        callback_data="notifon",
                    )
                ],
                [InlineKeyboardButton("❎", callback_data="closeMeh")],
            ]
        ),
    )


@Bot.on_message(filters.private & filters.command("broadcast"))
async def broadcast_handler_open(_, m):
    if m.from_group.id not in AUTH_USERS:
        await m.delete()
        return
    if m.reply_to_message is None:
        await m.delete()
    else:
        await broadcast(m, db)


@Bot.on_message(filters.private & filters.command("stats"))
async def sts(c, m):
    if m.from_group.id not in AUTH_USERS:
        await m.delete()
        return
    await m.reply_text(
        text=f"**Total Groups in Database 📂:** `{await db.total_groups_count()}`\n\n**Total Groups with Notification Enabled 🔔 :** `{await db.total_notif_groups_count()}`",
        quote=True
    )


@Bot.on_message(filters.private & filters.command("ban_group"))
async def ban(c, m):
    if m.from_group.id not in AUTH_USERS:
        await m.delete()
        return
    if len(m.command) == 1:
        await m.reply_text(
            f"Use this command to ban 🛑 any group from the bot 🤖.\n\nUsage:\n\n`/ban_group group_id ban_duration ban_reason`\n\nEg: `/ban_group 1234567 28 You misused me.`\n This will ban group with id `1234567` for `28` days for the reason `You misused me`.",
            quote=True,
        )
        return

    try:
        group_id = int(m.command[1])
        ban_duration = int(m.command[2])
        ban_reason = " ".join(m.command[3:])
        ban_log_text = f"Banning group {group_id} for {ban_duration} days for the reason {ban_reason}."

        try:
            await c.send_message(
                group_id,
                f"You are Banned 🚫 to use this bot for **{ban_duration}** day(s) for the reason __{ban_reason}__ \n\n**Message from the admin 🤠**",
            )
            ban_log_text += "\n\nGroup notified successfully!"
        except BaseException:
            traceback.print_exc()
            ban_log_text += (
                f"\n\n ⚠️ Group notification failed! ⚠️ \n\n`{traceback.format_exc()}`"
            )
        await db.ban_group(group_id, ban_duration, ban_reason)
        print(ban_log_text)
        await m.reply_text(ban_log_text, quote=True)
    except BaseException:
        traceback.print_exc()
        await m.reply_text(
            f"Error occoured ⚠️! Traceback given below\n\n`{traceback.format_exc()}`",
            quote=True
        )


@Bot.on_message(filters.private & filters.command("unban_group"))
async def unban(c, m):
    if m.from_group.id not in AUTH_USERS:
        await m.delete()
        return
    if len(m.command) == 1:
        await m.reply_text(
            f"Use this command to unban 😃 any group.\n\nUsage:\n\n`/unban_group group_id`\n\nEg: `/unban_group 1234567`\n This will unban group with id `1234567`.",
            quote=True,
        )
        return

    try:
        group_id = int(m.command[1])
        unban_log_text = f"Unbanning group 🤪 {group_id}"

        try:
            await c.send_message(group_id, f"Your ban was lifted!")
            unban_log_text += "\n\n✅ Group notified successfully! ✅"
        except BaseException:
            traceback.print_exc()
            unban_log_text += (
                f"\n\n⚠️ Group notification failed! ⚠️\n\n`{traceback.format_exc()}`"
            )
        await db.remove_ban(group_id)
        print(unban_log_text)
        await m.reply_text(unban_log_text, quote=True)
    except BaseException:
        traceback.print_exc()
        await m.reply_text(
            f"⚠️ Error occoured ⚠️! Traceback given below\n\n`{traceback.format_exc()}`",
            quote=True,
        )


@Bot.on_message(filters.private & filters.command("banned_groups"))
async def _banned_usrs(c, m):
    if m.from_group.id not in AUTH_USERS:
        await m.delete()
        return
    all_banned_groups = await db.get_all_banned_groups()
    banned_usr_count = 0
    text = ""
    async for banned_group in all_banned_groups:
        group_id = banned_group["id"]
        ban_duration = banned_group["ban_status"]["ban_duration"]
        banned_on = banned_group["ban_status"]["banned_on"]
        ban_reason = banned_group["ban_status"]["ban_reason"]
        banned_usr_count += 1
        text += f"> **Group_id**: `{group_id}`, **Ban Duration**: `{ban_duration}`, **Banned on**: `{banned_on}`, **Reason**: `{ban_reason}`\n\n"
    reply_text = f"Total banned group(s) 🤭: `{banned_usr_count}`\n\n{text}"
    if len(reply_text) > 4096:
        with open("banned-groups.txt", "w") as f:
            f.write(reply_text)
        await m.reply_document("banned-groups.txt", True)
        os.remove("banned-groups.txt")
        return
    await m.reply_text(reply_text, True)


@Bot.on_callback_query()
async def callback_handlers(bot: Client, cb: CallbackQuery):
    group_id = cb.from_group.id
    if cb.data == "notifon":
        notif = await db.get_notif(cb.from_group.id)
        if notif is True:
            await db.set_notif(group_id, notif=False)
        else:
            await db.set_notif(group_id, notif=True)
        await cb.message.edit(
            f"`Here You Can Set Your Settings:`\n\nSuccessfully setted notifications to **{await db.get_notif(group_id)}**",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            f"NOTIFICATION  {'🔔' if ((await db.get_notif(group_id)) is True) else '🔕'}",
                            callback_data="notifon",
                        )
                    ],
                    [InlineKeyboardButton("❎", callback_data="closeMeh")],
                ]
            ),
        )
        await cb.answer(
            f"Successfully setted notifications to {await db.get_notif(group_id)}"
        )
    else:
        await cb.message.delete(True)


Bot.run()
