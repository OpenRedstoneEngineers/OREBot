# Utility methods

class Message(object):
    """An object-oriented representation of an IRC protocol message"""

    def __init__(self, msg):
        self.msg = msg

        words = msg.split(" ")

        if words[0].startswith(":"):
            self.sender = words.pop(0)[1:]
        else:
            self.sender = None

        self.sendername = nameof(self.sender)

        self.command = words.pop(0).upper()

        self.args = []
        while words:
            if (words[0].startswith(":")):
                self.args.append(" ".join(words)[1:])
                break
            self.args.append(words.pop(0))


    def __str__(self):
        return self.msg

def nameof(sender):
    """Parses a message prefix and returns the sender's name."""

    if sender is None:
        return None
    else:
        return sender.partition("!")[0]
