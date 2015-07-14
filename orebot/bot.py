#!/usr/bin/env python3

import getpass
import socket

from orebot import hooks
from orebot import commands

class OREBot(object):
    def __init__(
            self, nickname="OREBot", password=None, ident_password=None, \
            hostname="irc.openredstone.org", port=6667, \
            channels=["#openredstone"], \
            services=["OREBuild", "ORESchool", "ORESurvival"], cmd="!"):
        self._sock = None
        self._sockfile = None
        self._connected = False
        self._msgbuffer = []

        self.nickname = nickname
        self.password = password
        self.ident_password = ident_password
        self.hostname = hostname
        self.port = port
        self.channels = channels
        self.services = services
        self.cmd = cmd


    def connect(self):
        print("Connecting to server at {}:{}".format(self.hostname, self.port))

        self._sock = socket.socket()
        self._sock.setblocking(True)
        self._sock.connect((self.hostname, self.port))
        self._sockfile = self._sock.makefile(encoding="utf-8")
        self._connected = True

        if self.password:
            self._sendmsg("PASS :{}".format(self.password))
        self._sendmsg("NICK {}".format(self.nickname))
        self._sendmsg("USER {} 0 * :ORE Utility Bot".format(getpass.getuser()))
        if self.ident_password:
            self._sendmsg("PRIVMSG NickServ :identify {}".format(
                self.ident_password))
        self._sendmsg("JOIN {}".format(",".join(self.channels)))


    def disconnect(self):
        print ("Disconnecting from server")

        self._sockfile.close()
        self._sock.close()
        self._sockfile = None
        self._sock = None
        self._connected = False


    def privmsg(self, target, msg):
        print("[{} -> {}] {}".format(self.nickname, target, msg))
        if isinstance(target, list):
            target = ",".join(target)
        self._sendmsg("PRIVMSG {} :{}".format(target, msg))


    def kick(self, target, channel, msg):
        print("{} has kicked {} from {}".format(
            self.nickname, target, channel))
        self._sendmsg("KICK {} {} :{}".format(target, channel, msg))


    def run(self):
        try:
            if not self._connected:
                self.connect()

            while self._connected:
                msg = self._recvmsg()
                self.handle(msg)
        finally:
            if self._connected:
                self.disconnect()


    def handle(self, msg):
        original = msg[0]
        sender = msg[1]
        command = msg[2]
        args = msg[3]

        if command == "PING":
            self._sendmsg("PONG :{}".format(args[0]))

        elif command == "JOIN":
            name = nameof(sender)
            channel = args[0]
            print("{} has joined {}".format(name, channel))

        elif command == "PART":
            name = self._nameof(sender)
            channel = args[0]
            print("{} has left {}".format(name, channel))

        elif command == "KICK":
            name = nameof(sender)
            victim = args[0]
            channel = args[1]
            print("{} has kicked {} from {}".format(name, victim, channel))

        elif command == "QUIT":
            name = nameof(sender)
            print("{} has quit IRC".format(name))

        elif command == "KILL":
            name = nameof(sender)
            victim = args[0]
            print("{} has killed {}".format(name, victim))

        elif command == "NICK":
            name = nameof(sender)
            newname = args[0]
            print("{} is now known as {}".format(name, newname))

        elif command == "NOTICE":
            name = nameof(sender)
            target = args[0]
            message = args[1]
            print("[{} -> {}]! {}".format(name, target, message))

        elif command == "PRIVMSG":
            name = nameof(sender)
            target = args[0]
            message = args[1]
            print("[{} -> {}] {}".format(name, target, message))

            hooks.handle(self, name, target, message)

        elif command.isdigit():
            print(args[-1])

        else:
            print(original)


    def _recvmsg(self):
        msg = self._sockfile.readline().rstrip("\r\n")
        words = msg.split()

        if words[0].startswith(":"):
            sender = words.pop(0)[1:]
        else:
            sender = None

        cmd = words.pop(0).upper()

        args = []
        while words:
            if (words[0].startswith(":")):
                args.append(" ".join(words)[1:])
                break
            args.append(words.pop(0))

        return (msg, sender, cmd, args)


    def _sendmsg(self, msg):
        self._sock.send((msg + "\r\n").encode("utf-8"))


# Utility methods

def nameof(sender):
    """Parses a message prefix and returns the sender's name."""
    return sender.partition("!")[0]


# Standard hooks

@hooks.hook
def mention(client, sender, target, message):
    """Replies to a user who mentioned the bot's name."""
    if client.nickname.lower() in message.lower():
        client.privmsg(sender, "You called?")

spammers = {}
@hooks.hook
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


# Standard commands

@commands.command
def help(sender, sendmsg, label, args):
    """Provides a list of available commands."""

    if len(args) > 0:
        page = int(args[0]) - 1
    else:
        page = 0

    pages = len(commands) // 10 + 1
    sortcommands = sorted(commands.values(), key=lambda c: c.__name__.lower())

    sendmsg("-- Help (Page {} of {}) --".format(page + 1, pages))
    for i in range(10):
        if i >= len(commands):
            break
        command = sortcommands[i]
        sendmsg("{}: {}".format(command.__name__, command.__doc__))

@commands.command
def ping(sender, sendmsg, label, args):
    """Returns 'Pong!' to the sender."""
    sendmsg("Pong!")
