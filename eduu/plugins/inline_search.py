import html
from uuid import uuid4

from hydrogram import Client
from hydrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
)

from eduu.utils import inline_commands
from eduu.utils.localization import use_chat_lang


@Client.on_inline_query(group=2)
@use_chat_lang
async def inline_search(c: Client, q: InlineQuery, strings):
    command = q.query.split(maxsplit=1)[0] if q.query else q.query

    results = inline_commands.search_commands(command)
    if not results:
        await q.answer(
            [
                InlineQueryResultArticle(
                    title=strings("inline_cmds_no_results").format(query=command),
                    input_message_content=InputTextMessageContent(
                        strings("inline_cmds_no_results").format(query=command)
                    ),
                )
            ],
            cache_time=0,
        )
        return

    articles = []
    for result in results:
        stripped_command = result["command"].split()[0]
        articles.append(
            InlineQueryResultArticle(
                id=uuid4(),
                title=result["command"],
                description=strings(result["description_key"]),
                input_message_content=InputTextMessageContent(
                    f"{html.escape(result['command'])}: {strings(result['description_key'])}"
                ),
                reply_markup=InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton(
                            text=strings("inline_cmds_run_command_button").format(
                                query=stripped_command
                            ),
                            switch_inline_query_current_chat=stripped_command,
                        )
                    ]
                ]),
            )
        )
    await q.answer(articles, cache_time=0)
