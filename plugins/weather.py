from config import prefix
from utils import http
from localization import GetLang
from pyrogram import Client, filters
from pyrogram.types import Message

# Api key used in weather.com's mobile app.
weather_apikey = "8de2d8b3a93542c9a2d8b3a935a2c909"

get_coords = "https://api.weather.com/v3/location/search"
url = "https://api.weather.com/v3/aggcommon/v3-wx-observations-current"

headers = {"User-Agent": "curl/7.72.0"}


@Client.on_message(filters.command(["clima", "weather"], prefix))
async def weather(c: Client, m: Message):
    _ = GetLang(m).strs
    if len(m.command) == 1:
        await m.reply_text(_("weather.weather_usage"))
    else:
        r = await http.get(get_coords, headers=headers,
                           params=dict(apiKey=weather_apikey,
                                       format="json",
                                       language=_("weather.weather_language"),
                                       query=m.text.split(maxsplit=1)[1]))
        loc_json = r.json()
        if not loc_json.get("location"):
            await m.reply_text(_("weather.location_not_found"))
        else:
            pos = f"{loc_json['location']['latitude'][0]},{loc_json['location']['longitude'][0]}"
            r = await http.get(url, headers=headers,
                               params=dict(apiKey=weather_apikey,
                                           format="json",
                                           language=_("weather.weather_language"),
                                           geocode=pos,
                                           units=_("weather.temperature_unit")))
            res_json = r.json()

            obs_dict = res_json["v3-wx-observations-current"]

            res = _("weather.details").format(location=loc_json["location"]["address"][0],

                                              temperature=obs_dict["temperature"],
                                              feels_like=obs_dict["temperatureFeelsLike"],
                                              air_humidity=obs_dict["relativeHumidity"],
                                              wind_speed=obs_dict["windSpeed"],
                                              overview=obs_dict["wxPhraseLong"])

            await m.reply_text(res, parse_mode="markdown")
