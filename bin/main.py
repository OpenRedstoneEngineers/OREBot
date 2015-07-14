#!/usr/bin/env python3

import json
import os

from orebot import bot

if os.path.isfile("./config.json"):
    with open("./config.json", "r") as f:
        config = json.load(f)
else:
    config = {}

client = bot.OREBot(**config)
client.run()
