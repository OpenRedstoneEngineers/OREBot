#!/usr/bin/env python3

import getpass
import json
import os
import socket

import hooks

class IRCClient(object):
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
        print("[{} has kicked {} from {}]".format(
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

def nameof(sender):
    return sender.partition("!")[0]

# Begin main

if os.path.isfile("./config.json"):
    with open("./config.json", "r") as f:
        config = json.load(f)
else:
    config = {}

client = IRCClient(**config)
client.run()
