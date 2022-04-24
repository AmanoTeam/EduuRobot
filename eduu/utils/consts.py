# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2022 Amano Team

from typing import Iterable

from pyrogram.enums import ChatMemberStatus, ChatType

group_types: Iterable[ChatType] = (ChatType.GROUP, ChatType.SUPERGROUP)

admin_status: Iterable[ChatMemberStatus] = (
    ChatMemberStatus.OWNER,
    ChatMemberStatus.ADMINISTRATOR,
)


class Permissions:
    can_be_edited: str = "can_be_edited"
    delete_messages: str = "can_delete_messages"
    restrict_members: str = "can_restrict_members"
    promote_members: str = "can_promote_members"
    change_info: str = "can_change_info"
    invite_users: str = "can_invite_users"
    pin_messages: str = "can_pin_messages"
