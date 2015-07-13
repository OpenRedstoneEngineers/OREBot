hooks = []

def hook(fun):
    hooks.append(fun)
    return fun

def handle(client, sender, target, message):
    for hook in hooks:
        hook(client, sender, target, message)

# Begin hooks

@hook
def mention(client, sender, target, message):
    """Replies to a user who mentioned the bot's name."""
    if client.nickname.lower() in message.lower():
        client.privmsg(sender, "You called?")

spammers = {}
@hook
def spam(client, sender, target, message):
    """Detects spammers and removes them from the channel."""
    if sender in client.services:
        return
    if sender not in spammers or message != spammers[sender][0]:
        spammers[sender] = [message, 0]
    else:
        spammers[sender][1] += 1

    if spammers[sender][1] == 1:
        client.privmsg(sender, \
                "WARNING: Spam detected. Stop or you will be kicked.")
    if spammers[sender][1] >= 4:
        for channel in client.channels:
            client.kick(sender, channel, "spam")
