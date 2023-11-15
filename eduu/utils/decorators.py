# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2023 Amano LLC

import asyncio
from functools import partial, wraps
from typing import Callable, Optional, Union

from pyrogram import Client, StopPropagation
from pyrogram.enums import ChatType
from pyrogram.types import CallbackQuery, ChatPrivileges, Message

from eduu.utils.localization import (
    default_language,
    get_lang,
    get_locale_string,
    langdict,
)
from eduu.utils.utils import check_perms


def aiowrap(func: Callable) -> Callable:
    @wraps(func)
    async def run(*args, loop=None, executor=None, **kwargs):
        if loop is None:
            loop = asyncio.get_event_loop()
        pfunc = partial(func, *args, **kwargs)
        return await loop.run_in_executor(executor, pfunc)

    return run


def require_admin(
    permissions: Optional[ChatPrivileges] = None,
    allow_in_private: bool = False,
    complain_missing_perms: bool = True,
):
    """Decorator that checks if the user is an admin in the chat.

    Parameters
    ----------
    permissions: ChatPrivileges
        The permissions to check for.
    allow_in_private: bool
        Whether to allow the command in private chats or not.
    complain_missing_perms: bool
        Whether to complain about missing permissions or not, otherwise the
        function will not be called and the user will not be notified.

    Returns
    -------
    Callable
        The decorated function.
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(client: Client, message: Union[CallbackQuery, Message], *args, **kwargs):
            lang = await get_lang(message)
            strings = partial(
                get_locale_string,
                langdict[lang].get("admins", langdict[default_language]["admins"]),
                lang,
                "admins",
            )

            if isinstance(message, CallbackQuery):
                sender = partial(message.answer, show_alert=True)
                msg = message.message
            elif isinstance(message, Message):
                sender = message.reply_text
                msg = message
            else:
                raise NotImplementedError(
                    f"require_admin can't process updates with the type '{message.__name__}' yet."
                )

            # We don't actually check private and channel chats.
            if msg.chat.type == ChatType.PRIVATE:
                if allow_in_private:
                    return await func(client, message, *args, *kwargs)
                return await sender(strings("private_not_allowed"))
            if msg.chat.type == ChatType.CHANNEL:
                return await func(client, message, *args, *kwargs)
            has_perms = await check_perms(message, permissions, complain_missing_perms, strings)
            if has_perms:
                return await func(client, message, *args, *kwargs)
            return None

        return wrapper

    return decorator


def stop_here(func: Callable) -> Callable:
    async def wrapper(*args, **kwargs):
        try:
            await func(*args, **kwargs)
        finally:
            raise StopPropagation

    return wrapper
