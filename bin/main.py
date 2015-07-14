#!/usr/bin/env python3

from orebot import bot

if os.path.isfile("./config.json"):
    with open("./config.json", "r") as f:
        config = json.load(f)
else:
    config = {}

client = bot.OREBot(**config)
client.run()
