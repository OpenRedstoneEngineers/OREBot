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

    if not message.startswith(bot.cmd):
        return

    words = message.split()

    if msg.sender in bot.services:
        sender = words.pop(0)[:-1]
    else:
        sender = msg.sender

    msgsendername = msg.sendername
    sendername = util.nameof(sender)

    label = words[0][len(bot.cmd):]
    args = words[1:]

    if label.lower() in commands:
        commands[label.lower()](bot, msgsendername, sendername, label, args)
