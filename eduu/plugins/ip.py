# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2024 Amano LLC

import ipaddress
import re

from hydrogram import Client, filters
from hydrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
    Message,
)
from yarl import URL

from config import PREFIXES
from eduu.utils import commands, http, inline_commands
from eduu.utils.localization import use_chat_lang


async def get_api_return(ip: str) -> dict[str, str]:
    r = await http.get(f"https://ipinfo.io/{ip}/json")
    req = r.json()
    req.pop("readme", None)

    return req


def format_api_return(req: dict[str, str], strings) -> str:
    if req.get("bogon"):
        return strings("ip_err_bogon_ip").format(ip=req["ip"])

    return "\n".join(f"<b>{i.title()}</b>: <code>{req[i]}</code>" for i in req)


async def resolve_hostname(hostname: str) -> list[str]:
    v4r = await http.get(
        f"https://cloudflare-dns.com/dns-query?name={hostname}&type=A",
        headers={"accept": "application/dns-json"},
    )
    v6r = await http.get(
        f"https://cloudflare-dns.com/dns-query?name={hostname}&type=AAAA",
        headers={"accept": "application/dns-json"},
    )

    v4j = v4r.json()
    v6j = v6r.json()

    answer = []

    if v6j.get("Answer"):
        answer.extend([i["data"] for i in v6j["Answer"] if i["type"] == 28])
    if v4j.get("Answer"):
        answer.extend([i["data"] for i in v4j["Answer"] if i["type"] == 1])

    return answer


async def get_ips_from_string(hostname: str) -> list[str]:
    try:
        # Check if it's an IP address
        parsed = ipaddress.ip_address(hostname)

        return [str(parsed)]
    except ValueError:
        # If not, check if it's a URL and get the host
        parsed = URL(hostname)
        if not parsed.is_absolute():
            parsed = URL(f"http://{hostname}")
        parsed = parsed.host

        # again, check if it's an IP address
        try:
            parsed = ipaddress.ip_address(parsed)

            return [str(parsed)]
        except ValueError:
            # If not, it's a domain name and will be resolved
            return await resolve_hostname(parsed)


@Client.on_message(filters.command("ip", PREFIXES))
@use_chat_lang
async def ip_cmd(c: Client, m: Message, strings):
    if len(m.text.split()) == 1:
        await m.reply_text(strings("ip_err_no_ip"))
        return

    text = m.text.split(maxsplit=1)[1]

    ips = await get_ips_from_string(text)

    if not ips:
        await m.reply_text(strings("ip_err_no_ips").format(domain=text))
        return

    if len(ips) == 1:
        await m.reply_text(format_api_return(await get_api_return(ips[0]), strings))
        return

    await m.reply_text(
        strings("ip_select_ip").format(domain=text),
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    ip,
                    callback_data=f"ip {ip}",
                )
            ]
            for ip in ips
        ]),
    )


@Client.on_callback_query(filters.regex(r"^ip .+"))
@use_chat_lang
async def ip_callback(c: Client, cb: CallbackQuery, strings):
    ip = cb.data.split(maxsplit=1)[1]

    await cb.edit_message_text(format_api_return(await get_api_return(ip), strings))


@Client.on_inline_query(filters.regex(r"^ip .+", re.IGNORECASE))
@use_chat_lang
async def ip_inline(c: Client, q: InlineQuery, strings):
    if len(q.query.split()) == 1:
        await q.answer([
            InlineQueryResultArticle(
                title=strings("ip_no_url"),
                input_message_content=InputTextMessageContent(
                    strings("ip_no_url_example").format(bot_username=c.me.username),
                ),
            )
        ])
        return

    text = q.query.split(maxsplit=1)[1]

    ips = await get_ips_from_string(text)

    if not ips:
        articles = [
            InlineQueryResultArticle(
                title=strings("ip_err_no_ips").format(domain=text),
                input_message_content=InputTextMessageContent(
                    strings("ip_err_no_ips").format(domain=text),
                ),
            )
        ]

    elif len(ips) == 1:
        api_return = await get_api_return(ips[0])

        articles = [
            InlineQueryResultArticle(
                title=strings("api_err_bogon_ip_inline").format(ip=ips[0])
                if api_return.get("bogon")
                else strings("ip_info_inline").format(domain=text),
                input_message_content=InputTextMessageContent(
                    format_api_return(api_return, strings),
                ),
            )
        ]
    else:
        articles = [
            InlineQueryResultArticle(
                title=strings("ip_select_ip").format(domain=text),
                input_message_content=InputTextMessageContent(
                    strings("ip_select_ip").format(domain=text),
                ),
                reply_markup=InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton(
                            ip,
                            callback_data=f"ip {ip}",
                        )
                    ]
                    for ip in ips
                ]),
            )
        ]
        articles.extend([
            InlineQueryResultArticle(
                title=ip,
                input_message_content=InputTextMessageContent(
                    format_api_return(await get_api_return(ip), strings),
                ),
            )
            for ip in ips
        ])

    await q.answer(
        articles,
        cache_time=0,
    )


commands.add_command("ip", "tools")
inline_commands.add_command("ip <host>")
