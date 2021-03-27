from pyrogram import Client, filters
from pyrogram.types import (
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
)
from pyrogram.errors import PeerIdInvalid, UsernameInvalid, UserIdInvalid


@Client.on_inline_query(filters.regex(r"^face"))
async def faces_inline(c: Client, q: InlineQuery):
    faces_list = [
        "¯\\_(ツ)_/¯",
        "( ͡° ͜ʖ ͡°)",
        "( ͡~ ͜ʖ ͡°)",
        "( ͡◐ ͜ʖ ͡◑))",
        "( ͡◔ ͜ʖ ͡◔)",
        "( ͡⚆ ͜ʖ ͡⚆)",
        "( ͡ʘ ͜ʖ ͡ʘ)",
        "ヽ༼ຈل͜ຈ༽ﾉ",
        "༼ʘ̚ل͜ʘ̚༽",
        "(╯°□°）╯",
        "(ﾉ◕ヮ◕)ﾉ",
        "(ﾉ◕ヮ◕)ﾉ*:･ﾟ✧",
        "(◕‿◕)",
        "(｡◕‿‿◕｡)",
        "(っ◕‿◕)っ",
        "(づ｡◕‿‿◕｡)づ",
        "༼ つ ◕_◕ ༽つ",
        "(ง ͠° ͟ل͜ ͡°)ง",
        "(ง'̀-'́)ง",
        "ᕙ(⇀‸↼‶)ᕗ",
        "(҂⌣̀_⌣́)",
        "ᕦ(ò_óˇ)ᕤ",
        "╚(ಠ_ಠ)=┐",
        "ლ(ಠ益ಠლ)",
        "\\_(ʘ_ʘ)_/",
        "( ⚆ _ ⚆ )",
        "(ಥ﹏ಥ)",
        "﴾͡๏̯͡๏﴿",
        "(◔̯◔)",
        "(ಠ_ಠ)",
        "(ಠ‿ಠ)",
        "(¬_¬)",
        "(¬‿¬)",
        "\\ (•◡•) /",
        "(◕‿◕✿)",
        "( ͡°( ͡° ͜ʖ( ͡° ͜ʖ ͡°)ʖ ͡°) ͡°)",
    ]
    results = []
    for i in faces_list:
        results.append(
            InlineQueryResultArticle(
                title=i, input_message_content=InputTextMessageContent(i)
            )
        )
    await q.answer(results)


@Client.on_inline_query(filters.regex(r"^markdown"))
async def markdown_inline(c: Client, q: InlineQuery):
    await q.answer(
        [
            InlineQueryResultArticle(
                title="click here to send the text in markdown format",
                input_message_content=InputTextMessageContent(
                    q.query.lower().split(None, 1)[1], parse_mode="markdown"
                ),
            )
        ]
    )


@Client.on_inline_query(filters.regex(r"^html"))
async def html_inline(c: Client, q: InlineQuery):
    await q.answer(
        [
            InlineQueryResultArticle(
                title="click here to send the text in html format",
                input_message_content=InputTextMessageContent(
                    q.query.lower().split(None, 1)[1], parse_mode="html"
                ),
            )
        ]
    )


@Client.on_inline_query(filters.regex(r"^info"))
async def info_inline(c: Client, q: InlineQuery):
    try:
        if q.query == "info":
            user = q.from_user
        elif q.query.lower().split(None, 1)[1]:
            txt = q.query.lower().split(None, 1)[1]
            user = await c.get_users(txt)
    except (PeerIdInvalid, UsernameInvalid, UserIdInvalid):
        await q.answer(
            [
                InlineQueryResultArticle(
                    title="i cant found the user",
                    input_message_content=InputTextMessageContent(
                        "i cant found the user"
                    ),
                )
            ]
        )
    await q.answer(
        [
            InlineQueryResultArticle(
                title="click here to get the information about the user",
                input_message_content=InputTextMessageContent(
                    f"username: {user.username} \n id: {user.id} \n dc: {user.dc_id} \n link to the user: {user.mention()}",
                ),
            )
        ]
    )
