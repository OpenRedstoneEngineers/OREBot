#!/usr/bin/env python3

import json
import os
import sys

from orebot import bot

if os.path.isfile("./config.json"):
    with open("./config.json", "r") as f:
        config = json.load(f)
else:
    config = {}

if "raygun_key" in config:
    raygun_key = config.pop("raygun_key")
else:
    raygun_key = None

if raygun_key is not None:
    from raygun4py import raygunprovider

    def handle_exception(exc_type, exc_value, exc_traceback):
        c = raygunprovider.RaygunSender(raygun_key)
        c.send_exception(exc_info=(exc_type, exc_value, exc_traceback))
        print("Error has been reported to Raygun")
    sys.excepthook = handle_exception

bot = bot.OREBot(**config)
bot.run()
