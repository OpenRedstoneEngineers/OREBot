from orebot import hooks

commands = {}

def command(fun):
    """A decorator for defining commands."""
    def wrap(client, user, sender, label, args):
        def sendmsg(message):
            if user in client.services:
                client.privmsg(user, ".msg {} {}".format(sender, message))
            else:
                client.privmsg(user, message)
        try:
            fun(sender, sendmsg, label, args)
        except Exception as e:
            sendmsg("An error occurred while executing this command")
            raise e

    wrap.__name__ = fun.__name__
    wrap.__doc__ = fun.__doc__
    commands[fun.__name__.lower()] = wrap
    return wrap

@hooks.hook
def oncommand(client, user, target, message):
    """Handles command detection and parsing"""
    if not message.startswith(client.cmd):
        return

    words = message.split()

    if user in client.services:
        sender = words.pop(0)[:-1]
    else:
        sender = user

    label = words[0][len(client.cmd):]
    args = words[1:]

    commands[label.lower()](client, user, sender, label, args)
