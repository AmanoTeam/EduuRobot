import httpx
from config import prefix
from pyrogram import Client, filters
from pyrogram.types import Message

# Api key used in weather.com's mobile app.
weather_apikey = "8de2d8b3a93542c9a2d8b3a935a2c909"

get_coords = "https://api.weather.com/v3/location/search"
url = "https://api.weather.com/v3/aggcommon/v3-wx-forecast-daily-15day-cognitiveHealth;vt1idxBreathingDaypart;v3-wx-conditions-historical-dailysummary-30day;vt1wwir;v3-wx-forecast-hourly-10day;vt1nowcast;v2idxRunDaypart5;vt1pastpollen;vt1contentMode;v3-location-point;vt1pollenobs;v3-wx-globalAirQuality;vt1currentTides;v3-wx-observations-current;v2idxDrySkinDaypart15;v3-wx-forecast-daily-15day;v3alertsHeadlines;vt1precipitation;vt1runweatherhourly"

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
            await m.reply_text("Localização não encontrada.")
        else:
            pos = f"{loc_json['location']['latitude'][0]},{loc_json['location']['longitude'][0]}"
            async with httpx.AsyncClient(http2=True) as http:
                r = await http.get(url, headers=headers,
                                   params=dict(apiKey=weather_apikey,
                                               format="json",
                                               language="pt-BR",
                                               pollenDays=0,
                                               pollenStartDate="20200830",
                                               geocode=pos,
                                               scale="EPA",
                                               conditionType="all",
                                               units="m"))
                res_json = r.json()

            obs_dict = res_json["v3-wx-observations-current"]

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
                 obs_dict["wxPhraseLong"])

            await m.reply_text(res, parse_mode="markdown")
