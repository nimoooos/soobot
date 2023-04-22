import discord  # interacts with discord messages
import time
from datetime import datetime
import requests
import json
import tokens

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)  # login to discord


async def cmd_sunlight(msg):
    """
    :param msg: discord message object
    :return: sunrise and sunset time
    """
    wordlist = msg.content[10:]  # cut off the command and look at parameter
    try:
        bing_maps = requests.get('http://dev.virtualearth.net/REST/v1/Locations/?query={}?&maxResults=1&key={}'.format(wordlist, tokens.BINGMAP))
        result = json.loads(bing_maps.content.decode('utf-8'))
        geocode_result = result['resourceSets'][0]['resources'][0]
        lat = float(geocode_result["point"]["coordinates"][0])
        lng = float(geocode_result["point"]["coordinates"][1])
        location = geocode_result["name"]

        response = requests.get('https://api.sunrise-sunset.org/json?lat={}&lng={}&formatted=0'.format(lat, lng))
        parsed_response = response.json()['results']

        unixtime_sunrise = int(datetime.strptime(parsed_response['sunrise'], '%Y-%m-%dT%H:%M:%S%z').timestamp())
        unixtime_sunset = int(datetime.strptime(parsed_response['sunset'], '%Y-%m-%dT%H:%M:%S%z').timestamp())

        msg_to_send = "Sunrise/sunset time from <https://sunrise-sunset.org/api>\n" \
                      + "Geocoding from Bing Maps\n" \
                      + "Location: {}\n".format(location) \
                      + "Coordinate: {}, {}\n".format(lat, lng) \
                      + "Sunrise: <t:{}>\n".format(unixtime_sunrise) \
                      + "Sunset: <t:{}>".format(unixtime_sunset)

        await msg.channel.send(msg_to_send)
        return

    except:
        await msg.channel.send("Invalid query, please be more specific.")
        return


async def cmd_whereis(msg):
    """
    :param msg: discord message object
    :return: print address and coordinate
    """
    wordlist = msg.content[9:]
    try:
        bing_maps = requests.get('http://dev.virtualearth.net/REST/v1/Locations/?query={}?&maxResults=1&key={}'.format(wordlist, tokens.BINGMAP))
        result = json.loads(bing_maps.content.decode('utf-8'))
        geocode_result = result['resourceSets'][0]['resources'][0]

        await msg.channel.send("{}".format(geocode_result['address']['formattedAddress']) +
                               ' is located at {}'.format(geocode_result['point']['coordinates']))
        return

    except:
        await msg.channel.send("Invalid query, please be more specific.")
        return


async def cmd_unixtime(msg):
    """
    input: $unixtime X
    output: for X=now, print unix time for now
    :param msg:
    :return:
    """

    wordlist = msg.content.split()
    if wordlist[1] == "now":
        # $unixtime now --> print present unix time
        now = int(time.time())
        await msg.channel.send("Unix timestamp for <t:{}>: {}".format(now, now))
    return


async def cmd_whatTimeIsIt(msg):
    wordlist = msg.content[14:]
    bing_maps = requests.get(
        'http://dev.virtualearth.net/REST/v1/Locations/?query={}?&maxResults=1&key={}'.format(wordlist, tokens.BINGMAP))
    result = json.loads(bing_maps.content.decode('utf-8'))
    geocode_result = result['resourceSets'][0]['resources'][0]
    address = geocode_result['address']['formattedAddress']
    lat = geocode_result['point']['coordinates'][0]
    lng = geocode_result['point']['coordinates'][1]

    local_time = requests.get(
        ('https://www.timeapi.io/api/Time/current/coordinate?latitude={}&longitude={}'
         .format(lat, lng))).json()

    await msg.channel.send("The local time at {} is {} {} {}"
                           .format(address, local_time['dayOfWeek'], local_time['date'], local_time['time']))
    return


async def cmd_activation_phrase(msg):
    """
    triggers when there's no commands triggered
    :param msg:
    :return:
    """

    # holds message
    query = msg.content.lower()

    # suicide hotline
    trigger_words = ("suicide", "suicidal", "unalive", "kms", "kill myself", "want to die")

    for i in trigger_words:
        if query.__contains__(i):
            await msg.channel.send("Hey <@{}>, are you alright?\n".format(msg.author.id) +
                                   "Here's the number to National Suicide Prevention Hotline: 1-800-273-8255")
            return

    # among us
    trigger_words = ("amogus", "among us", "among", "crewmate", "crew", "imposter", "impostor", "sabotage",
                     "sussy baka", "sussy", "sus", "venting", "vent")

    for i in trigger_words:
        if query.__contains__(i):
            await msg.channel.send(i + '??? Sus??? Amogus????')
            return

    return


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        # don't reply to self
        return

    # holds message
    print(message)
    query = message.content.lower()

    if query.startswith('$hello'):
        await message.channel.send('Hello! I am {0.user}'.format(client))

    elif query.startswith('$sunlight'):
        await cmd_sunlight(message)

    elif query.startswith('$whereis'):
        await cmd_whereis(message)

    elif query.startswith('$countdown'):
        await cmd_countdown(message)

    elif query.startswith('$invite'):
        invite_link = "https://discord.com/api/oauth2/authorize?client_id=945195795366420481&permissions=8&scope=bot"
        await message.channel.send("invite link: " + invite_link)

    elif query.startswith('$unixtime'):
        await cmd_unixtime(message)

    elif query.startswith('$whattimeat'):
        await cmd_whatTimeAt(message)

    else:
        await cmd_activation_phrase(message)

client.run(tokens.DISCORD)
