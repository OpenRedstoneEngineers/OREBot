from orebot import hooks
from orebot import util

commands = {}

def command(fun):
    """A decorator for defining commands."""

    def wrap(bot, user, sender, label, args):
        def sendmsg(message):
            if user in bot.services:
                bot.privmsg(user, ".msg {} {}".format(sender, message))
            else:
                bot.privmsg(user, message)
        try:
            fun(bot, sender, sendmsg, label, args)
        except Exception as e:
            sendmsg("An error occurred while executing this command")
            raise e

    wrap.__name__ = fun.__name__
    wrap.__doc__ = fun.__doc__
    commands[fun.__name__.lower()] = wrap
    return wrap

@hooks.hook
def oncommand(bot, msg):
    """Handles command detection and parsing"""

    if msg.command != "PRIVMSG":
        return

    target = msg.args[0]
    message = msg.args[1]

    words = message.split()

    if msg.sendername in bot.services:
        sender = words.pop(0)[:-1]
    else:
        sender = msg.sendername

    if len(words) < 1:
        return

    if not words[0].startswith(bot.cmd):
        return

    msgsender = msg.sendername

    label = words.pop(0)[len(bot.cmd):]
    args = words

    if label.lower() in commands:
        commands[label.lower()](bot, msgsender, sender, label, args)
