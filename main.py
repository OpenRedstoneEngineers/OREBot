#!/usr/bin/env python3

import getpass
import json
import os
import socket

class IRCClient:
    def __init__(
            self, nickname, password, ident_password, server, channels, \
            services, cmd):
        self._sock = None
        self._sockfile = None
        self._connected = False
        self._msgbuffer = []

        self.nickname = nickname
        self.password = password
        self.ident_password = ident_password
        self.server = server
        # Dictionary is used later for channel membership tracking
        self.channels = {}
        for chan in channels:
            self.channels[chan.lower()] = []
        self.services = services
        self.cmd = cmd

    def connect(self):
        print("Connecting to server at %s:%s" % self.server)

        self._sock = socket.socket()
        self._sock.setblocking(True)
        self._sock.connect(self.server)
        self._sockfile = self._sock.makefile(encoding="utf-8")
        self._connected = True

        if self.password:
            self._sendmsg("PASS :%s" % self.password)
        self._sendmsg("NICK %s" % self.nickname)
        self._sendmsg("USER %s 0 * :ORE Utility Bot" % getpass.getuser())
        if self.ident_password:
            self._sendmsg("PRIVMSG NickServ :identify %s" % self.ident_password)
        self._sendmsg("JOIN %s" % ",".join(self.channels.keys()))

    def disconnect(self):
        print ("Disconnecting from server")

        self._sockfile.close()
        self._sock.close()
        self._sockfile = None
        self._sock = None
        self._connected = False

    def run(self):
        try:
            if not self._connected:
                self.connect()

            while self._connected:
                msg = self._recvmsg()
                sender = msg[0]
                command = msg[1]
                args = msg[2]

                if command == "PING":
                    self._sendmsg("PONG :%s" % args[0])
        finally:
            if self._connected:
                self.disconnect()

    def _recvmsg(self):
        msg = self._sockfile.readline().rstrip("\r\n")
        print("< " + msg)
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

        return (sender, cmd, args)

    def _sendmsg(self, msg):
        self._sock.send((msg + "\r\n").encode("utf-8"))
        print("> " + msg)

# Begin main

if os.path.isfile("./config.json"):
    with open("./config.json", "r") as f:
        config = json.load(f)
else:
    with open("./config.default.json", "r") as f:
        config = json.load(f)

client = IRCClient(
    config["nickname"], config["password"], config["ident_password"], \
    (config["server"], config["port"]), config["channels"], \
    config["services"], config["cmd"])
client.run()
