# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2023 Amano LLC

from collections.abc import Iterable

from pyrogram.enums import ChatMemberStatus, ChatType

GROUP_TYPES: Iterable[ChatType] = (ChatType.GROUP, ChatType.SUPERGROUP)

ADMIN_STATUSES: Iterable[ChatMemberStatus] = (
    ChatMemberStatus.OWNER,
    ChatMemberStatus.ADMINISTRATOR,
)
