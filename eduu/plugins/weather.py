# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2023 Amano LLC

from config import PREFIXES
from pyrogram import Client, filters
from pyrogram.types import Message

from ..utils import commands, http
from ..utils.localization import use_chat_lang

# Api key used in weather.com's mobile app.
weather_apikey = "8de2d8b3a93542c9a2d8b3a935a2c909"

get_coords = "https://api.weather.com/v3/location/search"
url = "https://api.weather.com/v3/aggcommon/v3-wx-observations-current"

headers = {
    "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 12; M2012K11AG Build/SQ1D.211205.017)",
}

status_emojis = {
    0: "⛈",
    1: "⛈",
    2: "⛈",
    3: "⛈",
    4: "⛈",
    5: "🌨",
    6: "🌨",
    7: "🌨",
    8: "🌨",
    9: "🌨",
    10: "🌨",
    11: "🌧",
    12: "🌧",
    13: "🌨",
    14: "🌨",
    15: "🌨",
    16: "🌨",
    17: "⛈",
    18: "🌧",
    19: "🌫",
    20: "🌫",
    21: "🌫",
    22: "🌫",
    23: "🌬",
    24: "🌬",
    25: "🌨",
    26: "☁️",
    27: "🌥",
    28: "🌥",
    29: "⛅️",
    30: "⛅️",
    31: "🌙",
    32: "☀️",
    33: "🌤",
    34: "🌤",
    35: "⛈",
    36: "🔥",
    37: "🌩",
    38: "🌩",
    39: "🌧",
    40: "🌧",
    41: "❄️",
    42: "❄️",
    43: "❄️",
    44: "n/a",
    45: "🌧",
    46: "🌨",
    47: "🌩",
}


def get_status_emoji(status_code: int) -> str:
    return status_emojis.get(status_code, "n/a")


@Client.on_message(filters.command(["clima", "weather"], PREFIXES))
@use_chat_lang()
async def weather(c: Client, m: Message, strings):
    if len(m.command) == 1:
        return await m.reply_text(strings("weather_usage"))

    r = await http.get(
        get_coords,
        headers=headers,
        params={
            "apiKey": weather_apikey,
            "format": "json",
            "language": strings("weather_language"),
            "query": m.text.split(maxsplit=1)[1],
        },
    )
    loc_json = r.json()
    if not loc_json.get("location"):
        await m.reply_text(strings("location_not_found"))
        return None
    else:
        pos = f"{loc_json['location']['latitude'][0]},{loc_json['location']['longitude'][0]}"
        r = await http.get(
            url,
            headers=headers,
            params={
                "apiKey": weather_apikey,
                "format": "json",
                "language": strings("weather_language"),
                "geocode": pos,
                "units": strings("measurement_unit"),
            },
        )
        res_json = r.json()

        obs_dict = res_json["v3-wx-observations-current"]

        res = strings("details").format(
            location=loc_json["location"]["address"][0],
            temperature=obs_dict["temperature"],
            feels_like=obs_dict["temperatureFeelsLike"],
            air_humidity=obs_dict["relativeHumidity"],
            wind_speed=obs_dict["windSpeed"],
            overview=f"{get_status_emoji(obs_dict['iconCode'])} {obs_dict['wxPhraseLong']}",
        )

        await m.reply_text(res)
        return None


commands.add_command("weather", "tools")
