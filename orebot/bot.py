#!/usr/bin/env python3

import builtins
import getpass
import socket

from orebot import commands
from orebot import hooks
from orebot import util

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
        """Connects to the server as defined in the bot's configuration."""

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


    def disconnect(self, reason=None):
        """Disconnects from the bot's current server."""

        print ("Disconnecting from server")

        if reason:
            reason = " :" + reason
        else:
            reason = ""

        self._sendmsg("QUIT" + reason)

        self._sockfile.close()
        self._sock.close()
        self._sockfile = None
        self._sock = None
        self._connected = False


    def privmsg(self, target, msg):
        """Sends a message to a user or channel on the current server."""

        if isinstance(target, list):
            target = ",".join(target)
        self._sendmsg("PRIVMSG {} :{}".format(target, msg))
        print("[{} -> {}] {}".format(self.nickname, target, msg))


    def broadcast(self, msg):
        self.privmsg(self.channels, msg)


    def kick(self, target, channel, msg):
        """Kicks a user from a channel, assuming the bot has permission to."""

        if isinstance(target, list)
            target = ",".join(target)
        if isinstance(channel, list)
            channel = ",".join(channel)

        self._sendmsg("KICK {} {} :{}".format(channel, target, msg))
        print("{} has kicked {} from {}".format(
            self.nickname, target, channel))


    def run(self):
        """Runs a loop that handles messages automatically until disconnect."""

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
        """Logs a message and sends it to registered hooks."""

        if msg.command == "PING":
            self._sendmsg("PONG :{}".format(msg.args[0]))

        elif msg.command == "JOIN":
            name = msg.sendername
            channel = msg.args[0]
            print("{} has joined {}".format(name, channel))

        elif msg.command == "PART":
            name = msg.sendername
            channel = msg.args[0]
            print("{} has left {}".format(name, channel))

        elif msg.command == "KICK":
            name = msg.sendername
            channel = msg.args[0]
            victim = msg.args[1]
            print("{} has kicked {} from {}".format(name, victim, channel))

        elif msg.command == "QUIT":
            name = msg.sendername
            print("{} has quit IRC".format(name))

        elif msg.command == "KILL":
            name = msg.sendername
            victim = msg.args[0]
            print("{} has killed {}".format(name, victim))

        elif msg.command == "NICK":
            name = msg.sendername
            newname = msg.args[0]
            print("{} is now known as {}".format(name, newname))

        elif msg.command == "MODE":
            name = msg.sendername
            target = msg.args[0]
            mode = msg.args[1]
            print("{} has set the mode of {} to {}".format(name, target, mode))

        elif msg.command == "NOTICE":
            name = msg.sendername
            target = msg.args[0]
            message = msg.args[1]
            print("[{} -> {}]! {}".format(name, target, message))

        elif msg.command == "PRIVMSG":
            name = msg.sendername
            target = msg.args[0]
            message = msg.args[1]
            print("[{} -> {}] {}".format(name, target, message))

        elif msg.command.isdigit():
            print(msg.args[-1])

        else:
            print(str(msg))

        hooks.handle(self, msg)


    def _recvmsg(self):
        msg = self._sockfile.readline().rstrip("\r\n")
        return util.Message(msg)


    def _sendmsg(self, msg):
        self._sock.send((msg + "\r\n").encode("utf-8"))


# Standard hooks

@hooks.hook
def mention(bot, msg):
    """Replies to a user who mentioned the bot's name."""

    if msg.command != "PRIVMSG":
        return

    message = msg.args[1]

    if bot.nickname.lower() in message.lower():
        bot.privmsg(msg.sendername, "You called?")

spammers = {}
@hooks.hook
def spam(bot, msg):
    """Detects spammers and removes them from the channel."""

    sendername = msg.sendername

    if msg.command != "PRIVMSG" or sendername in bot.services:
        return

    message = msg.args[1]

    if sendername not in spammers or message != spammers[sendername][0]:
        spammers[sendername] = [message, 0]
    else:
        spammers[sendername][1] += 1

    if spammers[sendername][1] == 1:
        bot.privmsg(msg.sendername, \
                "WARNING: Spam detected. Stop or you will be kicked.")
    if spammers[sendername][1] >= 4:
        for channel in bot.channels:
            bot.kick(msg.sendername, channel, "Spam detected")


# Standard commands

@commands.command
def help(bot, sender, sendmsg, label, args):
    """Provides a list of available commands."""

    clist = commands.commands
    csort = sorted(clist.values(), key=lambda c: c.__name__.lower())

    if len(args) > 0:
        page = int(args[0]) - 1
    else:
        page = 0

    pages = len(clist) // 10 + 1

    sendmsg("-- Help (Page {} of {}) --".format(page + 1, pages))
    for i in range(10):
        if i >= len(csort):
            break

        command = csort[i + (page * 10)]
        sendmsg("{}: {}".format(command.__name__, command.__doc__))

@commands.command
def ping(bot, sender, sendmsg, label, args):
    """Returns 'Pong!' to the sender."""

    sendmsg("Pong!")

@commands.command
def calc(bot, sender, sendmsg, label, args):
    """Evaluates a Python expression."""

    expr = " ".join(args)
    banned = dir() + dir(builtins)
    for word in banned:
        if word in expr:
            sendmsg("Illegal word found: " + word)
            return
    try:
        sendmsg(eval(expr))
    except Exception as e:
        sendmsg(str(e))


@commands.command
def welcome(bot, sender, sendmsg, label, args):
    """Welcomes a new player to ORE."""

    bot.broadcast("Welcome to ORE! In order to get a plot, you must apply.")
    bot.broadcast("See http://openredstone.org/apply for more details.")
