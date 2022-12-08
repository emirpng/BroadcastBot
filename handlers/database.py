# (c) N A C BOTS

import datetime

import motor.motor_asyncio


class Database:
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.col = self.db.groups

    def new_group(self, id):
        return dict(
            id=id,
            join_date=datetime.date.today().isoformat(),
            notif=True,
            ban_status=dict(
                is_banned=False,
                ban_duration=0,
                banned_on=datetime.date.max.isoformat(),
                ban_reason="",
            ),
        )

    async def add_group(self, id):
        group = self.new_group(id)
        await self.col.insert_one(group)

    async def is_group_exist(self, id):
        group = await self.col.find_one({"id": int(id)})
        return True if group else False

    async def total_groups_count(self):
        count = await self.col.count_documents({})
        return count

    async def get_all_groups(self):
        all_groups = self.col.find({})
        return all_groups

    async def delete_group(self, group_id):
        await self.col.delete_many({"id": int(group_id)})

    async def remove_ban(self, id):
        ban_status = dict(
            is_banned=False,
            ban_duration=0,
            banned_on=datetime.date.max.isoformat(),
            ban_reason="",
        )
        await self.col.update_one({"id": id}, {"$set": {"ban_status": ban_status}})

    async def ban_group(self, group_id, ban_duration, ban_reason):
        ban_status = dict(
            is_banned=True,
            ban_duration=ban_duration,
            banned_on=datetime.date.today().isoformat(),
            ban_reason=ban_reason,
        )
        await self.col.update_one({"id": group_id}, {"$set": {"ban_status": ban_status}})

    async def get_ban_status(self, id):
        default = dict(
            is_banned=False,
            ban_duration=0,
            banned_on=datetime.date.max.isoformat(),
            ban_reason="",
        )
        group = await self.col.find_one({"id": int(id)})
        return group.get("ban_status", default)

    async def get_all_banned_groups(self):
        banned_groups = self.col.find({"ban_status.is_banned": True})
        return banned_groups

    async def set_notif(self, id, notif):
        await self.col.update_one({"id": id}, {"$set": {"notif": notif}})

    async def get_notif(self, id):
        group = await self.col.find_one({"id": int(id)})
        return group.get("notif", False)

    async def get_all_notif_group(self):
        notif_groups = self.col.find({"notif": True})
        return notif_groups

    async def total_notif_groups_count(self):
        count = await self.col.count_documents({"notif": True})
        return count
