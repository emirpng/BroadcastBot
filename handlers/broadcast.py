# (c) N A C BOTS

import asyncio
import datetime
import os
import random
import string
import time
import traceback

import aiofiles
from pyrogram.errors import (
    FloodWait,
    InputUserDeactivated,
    PeerIdInvalid,
    UserIsBlocked,
)

import config

broadcast_ids = {}

BROADCAST_AS_COPY = config.BROADCAST_AS_COPY


async def send_msg(group_id, message):
    try:
        if BROADCAST_AS_COPY is False:
            await message.forward(chat_id=group_id)
        elif BROADCAST_AS_COPY is True:
            await message.copy(chat_id=group_id)
        return 200, None
    except FloodWait as e:
        await asyncio.sleep(e.x)
        return send_msg(group_id, message)
    except InputUserDeactivated:
        return 400, f"{group_id} : devre dışı bırakıldı\n"
    except UserIsBlocked:
        return 400, f"{group_id} : botu engelledi\n"
    except PeerIdInvalid:
        return 400, f"{group_id} : grup kimliği geçersiz\n"
    except Exception:
        return 500, f"{group_id} : {traceback.format_exc()}\n"


async def broadcast(m, db):
    all_groups = await db.get_all_notif_group()
    broadcast_msg = m.reply_to_message
    while True:
        broadcast_id = "".join([random.choice(string.ascii_letters) for i in range(3)])
        if not broadcast_ids.get(broadcast_id):
            break
    out = await m.reply_text(
        text=f"🦈⚡️ Yayın Başlatıldı! Tüm gruplar bilgilendirildiğinde günlük dosyası ile bilgilendirileceksiniz."
    )
    start_time = time.time()
    total_groups = await db.total_groups_count()
    done = 0
    failed = 0
    success = 0
    broadcast_ids[broadcast_id] = dict(
        total=total_groups, current=done, failed=failed, success=success
    )
    async with aiofiles.open("broadcast.txt", "w") as broadcast_log_file:
        async for group in all_groups:
            sts, msg = await send_msg(group_id=int(group["id"]), message=broadcast_msg)
            if msg is not None:
                await broadcast_log_file.write(msg)
            if sts == 200:
                success += 1
            else:
                failed += 1
            if sts == 400:
                await db.delete_group(group["id"])
            done += 1
            if broadcast_ids.get(broadcast_id) is None:
                break
            else:
                broadcast_ids[broadcast_id].update(
                    dict(current=done, failed=failed, success=success)
                )
    if broadcast_ids.get(broadcast_id):
        broadcast_ids.pop(broadcast_id)
    completed_in = datetime.timedelta(seconds=int(time.time() - start_time))
    await asyncio.sleep(3)
    await out.delete()
    if failed == 0:
        await m.reply_text(
            text=f"🦈⚡️ Yayın `{completed_in}` içinde tamamlandı.\n\nToplam Grup: {total_groups}.\nToplam Yayın: {done}, {success} başarılı ve {failed} başarısız.",
            quote=True,
        )
    else:
        await m.reply_document(
            document="broadcast.txt",
            caption=f"🦈⚡️ Yayın `{completed_in}` içinde tamamlandı.\n\nToplam Grup: {total_groups}.\nToplam Yayın: {done}, {success} başarılı ve {failed} başarısız.",
            quote=True,
        )
    os.remove("broadcast.txt")
