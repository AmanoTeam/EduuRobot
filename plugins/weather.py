import regex
import json
import httpx
from config import prefix
from pyrogram import Client, filters
from pyrogram.types import Message

# That api key were publicly shown some time ago, but it still works.
weather_apikey = "d522aa97197fd864d36b418f39ebb323"

get_coords = "https://api.weather.com/v3/location/search"
url = "https://weather.com/pt-BR/clima/hoje/l"

headers = {"User-Agent": "curl/7.72.0"}


@Client.on_message(filters.command(["clima", "weather"], prefix))
async def weather(c: Client, m: Message):
    if len(m.command) == 1:
        await m.reply_text("**Uso:** `/clima <cidade>` - __Obtem informações meteorológicas da cidade.__")
    else:
        async with httpx.AsyncClient(http2=True) as http:
            r = await http.get(get_coords, headers=headers,
                               params=dict(apiKey=weather_apikey,
                                           format="json",
                                           language="pt-BR",
                                           query=m.text.split(maxsplit=1)[1]))
            loc_json = r.json()
        if not loc_json.get("location"):
            await m.reply_text("Localização não encontrada")
        else:
            pos = loc_json["location"]["placeId"][0]
            async with httpx.AsyncClient(http2=True) as http:
                r = await http.get(f"{url}/{pos}", headers=headers)
            res_json = regex.findall(r"__data=JSON\.parse\(\"(.*)\"\);</script><script>window\.env", r.text)
            # If the returned list is empty...
            if not res_json:
                return await m.reply_text("Esta localização não possui dados meteorológicos.")
            res_json = json.loads(res_json[0].encode().decode("unicode_escape"))

            obs_key = next(iter(res_json["dal"]["getSunV3CurrentObservationsUrlConfig"]))
            obs_dict = res_json["dal"]["getSunV3CurrentObservationsUrlConfig"][obs_key]["data"]

            res = """**{}**:

Temperatura: `{} °C`
Sensação térmica: `{} °C`
Umidade do Ar: `{}%`
Vento: `{} km/h`

- __{}__""".format(loc_json["location"]["address"][0],

                 obs_dict["temperature"],
                 obs_dict["temperatureFeelsLike"],
                 obs_dict["relativeHumidity"],
                 obs_dict["windSpeed"],
                 obs_dict["cloudCoverPhrase"])

            await m.reply_text(res, parse_mode="markdown")
