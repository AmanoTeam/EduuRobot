# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2021 Amano Team

from tortoise import Tortoise, fields
from tortoise.models import Model


class groups(Model):
    chat_id = fields.IntField(pk=True)
    welcome = fields.TextField(null=True)
    welcome_enabled = fields.BooleanField(null=True)
    rules = fields.TextField(null=True)
    warns_limit = fields.IntField(null=True)
    chat_lang = fields.TextField(null=True)
    cached_admins = fields.TextField(null=True)
    antichannelpin = fields.BooleanField(null=True)
    delservicemsgs = fields.BooleanField(null=True)
    warn_action = fields.TextField(null=True)


class users(Model):
    user_id = fields.IntField(pk=True)
    chat_lang = fields.TextField(null=True)


class filters(Model):
    chat_id = fields.IntField()
    filter_name = fields.TextField()
    raw_data = fields.TextField(null=True)
    file_id = fields.TextField(null=True)
    filter_type = fields.TextField()


class notes(Model):
    chat_id = fields.IntField()
    note_name = fields.TextField()
    raw_data = fields.TextField(null=True)
    file_id = fields.TextField(null=True)
    note_type = fields.TextField()


class channels(Model):
    chat_id = fields.IntField(pk=True)
    chat_lang = fields.TextField(null=True)


class was_restarted_at(Model):
    chat_id = fields.IntField(null=True)
    message_id = fields.IntField(null=True)


class user_warns(Model):
    user_id = fields.IntField(null=True)
    chat_id = fields.IntField(null=True)
    count = fields.IntField(null=True)


async def init_database():
    await Tortoise.init(
        db_url="sqlite://eduu/database/eduu.db", modules={"models": [__name__]}
    )
    await Tortoise.generate_schemas()
