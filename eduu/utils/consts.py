# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2026 Amano LLC

from __future__ import annotations

from typing import TYPE_CHECKING

from hydrogram.enums import ChatMemberStatus, ChatType

if TYPE_CHECKING:
    from collections.abc import Iterable

GROUP_TYPES: Iterable[ChatType] = (ChatType.GROUP, ChatType.SUPERGROUP)

ADMIN_STATUSES: Iterable[ChatMemberStatus] = (
    ChatMemberStatus.OWNER,
    ChatMemberStatus.ADMINISTRATOR,
)
