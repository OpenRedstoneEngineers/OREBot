#!/usr/bin/env python3
import socket
import time
import keyword
import json
import os

class IRCClient:
    socket = None
    connected = False

    nickname = "OREBot"
    password = None
    ident_password = None
    server = "irc.freenode.net"
    port = 6667
    channels = {"#openredstone":[]}
    services = ["OREBuild","ORESchool","ORESurvival"]
    cmd = "!"

    def __init__(self):
        self.ctx = {}
        self.oldctx = {
            "sender"     : "",
            "sendername" : "",
            "type"       : "",
            "target"     : "",
            "msg"        : ""
        }
        self.spam2 = ""
        self.s = 0
        self.e = True
        self.bcolors = {
            "HEADER"    : "\033[95m",
            "OKBLUE"    : "\033[94m",
            "OKGREEN"   : "\033[92m",
            "WARNING"   : "\033[93m",
            "FAIL"      : "\033[91m",
            "ENDC"      : "\033[0m" ,
            "BOLD"      : "\033[1m" ,
            "UNDERLINE" : "\033[4m"
        }

    def start(self):
        self.socket = socket.socket()
        self.socket.connect((self.server, self.port))
        self.send("NICK %s" % self.nickname)
        self.send("USER %(nick)s %(nick)s %(nick)s :%(nick)s" % {"nick":self.nickname})
        while True:
            i=0
            buf = self.socket.recv(4096).decode("latin1")
            lines = buf.split("\n")
            for data in lines:
                data = str(data).strip()

                if data == "":
                    continue
                print ("I<", data)

                # server ping/pong?
                if data.find("PING") != -1:
                    n = data.split(":")[1]
                    self.send("PONG :" + n)
                    if self.connected == False:
                        self.perform()
                        self.connected = True

                args = data.split(None, 3)
                args1= data.split(None, 5)
                if len(args)<=1:
                    continue

                #managing user list
                if args1[1]=="353":
                    for c in self.channels:
                        if args1[4]==c:
                            for n in args1[5][1:].split():
                                if n.find("@") != -1:
                                    n=n[1:]
                                self.channels[c].append(n)
                        print (c, ": ", self.channels[c])
                    continue
                if args[1]=="JOIN" and self.channels[args[2]]!=[]:
                    self.channels[args[2]].append(args[0][1:].split("!",1)[0])
                    print (args[2], self.channels[args[2]])
                    continue
                if args1[1]=="KICK":
                    self.channels[args1[2]].remove(args1[3])
                    print (args[2], self.channels[args[2]])
                    continue
                if args[1]=="PART":
                    self.channels[args[2]].remove(args[0][1:].split("!",1)[0])
                    print (args[2], self.channels[args[2]])
                    continue
                if args[1]=="QUIT":
                    for c in self.channels:
                        try:
                            self.channels[c].remove(args[0].split("!")[0][1:])
                            print (c, self.channels[c])
                        except (ValueError):
                            pass
                    continue
                if args[1]=="NICK":
                    for c in self.channels:
                        i=0
                        for n in self.channels[c]:
                            if n==args[0][1:].split("!")[0]:
                                self.channels[c][i]==args[2]
                            i+=1
                        i=0
                    continue

                if args[1]!="PRIVMSG":
                    continue

                self.ctx = {}
                self.ctx["sender"]     = args[0][1:]
                self.ctx["sendername"] = args[0][1:].split("!")[0]
                self.ctx["type"]       = args[1]
                self.ctx["target"]     = args[2]
                self.ctx["msg"]         = args[3][1:]

                # Channel moderation
                # Spam kicking
                if self.oldctx["sender"]==self.ctx["sender"] and self.oldctx["msg"]==self.ctx["msg"] and not any(x==self.ctx["sendername"] for x in self.services):
                    self.s+=1
                    if self.s==1:
                        self.say("WARNING: spam detected from user %s. stop or you will be kicked" % self.ctx["sendername"], self.ctx["sendername"])
                        # slack alert goes here
                        modlog=open("moderationlog", "a")
                        modlog.write('%sWarned player %s for spam with "%s"\n' % (time.strftime("[%b %d %Y] - [%H:%M:%S]"), self.ctx["sendername"], self.ctx["msg"]))
                        modlog.close()
                    elif self.s==4:
                        for c in self.channels:
                            self.kick(c, self.ctx["sendername"], "spam")
                        # slack alert goes here
                        modlog=open("moderationlog", "a")
                        modlog.write('%sKicked player %s for spam with "%s"\n' % (time.strftime("[%b %d %Y] - [%H:%M:%S]"), self.ctx["sendername"], self.ctx["msg"]))
                        modlog.close()
                elif self.ctx["sendername"]==self.nickname:
                    pass
                else:
                    self.s=0

                # whom to reply?
                target = self.ctx["sendername"]
                if (self.ctx["msg"].find(":")==-1 and any(x==target for x in self.services)) or (self.ctx["msg"].find(":")==len(self.ctx["msg"])-1):
                    continue
                elif any(x==target for x in self.services):
                    fullcmd=self.ctx["msg"].split(": ",1)[1]
                else:
                    fullcmd=self.ctx["msg"]

                # commands
                # help command
                if fullcmd == "".join((self.cmd,"help")):
                    self.say("%s is a moderation tool to help keep the chat clean" % self.nickname, target)
                    self.say("available commands: !calc, !welcome", target)
                    self.say('type "!help <command> for details on a specific command', target)

                # help command for calc
                elif fullcmd == "".join((self.cmd, "help calc")):
                    self.say("syntax: !calc <expression>",target)
                    self.say("calculate an expression provided after the command",target)
                    self.say("currently unavailable",target)

                # help command for welcome
                elif fullcmd[0:len(self.cmd)+12] == "".join((self.cmd,"help welcome")):
                    self.say("syntax: !welcome <player_name>",target)
                    self.say("Welcome a player and provide said player with how to get started, how to apply, and a link to the ORE services.",target)

                # calc command
                elif fullcmd[0:len(self.cmd)+5] == "".join((self.cmd,"calc ")):
                    cmdargs=fullcmd.split(None,1)
                    if len(cmdargs)==1:
                        self.say("ArgumentError: expected 1 argument(s), got 0",target)
                    else:
                        self.say(self.calcexpression(cmdargs[1]),target)

                # welcome command
                elif fullcmd[0:len(self.cmd)+8] == "".join((self.cmd, "welcome ")):
                    cmdargs=fullcmd.split()
                    if len(cmdargs)!=2:
                        self.say("ArgumentError: expected 1 argument(s), got %s" % len(cmdargs)-1,target)
                    else:
                        target2=cmdargs[1]
                        self.say("Welcome to ORE, %s! In order to get started, you can teleport to the welcome signs using /welcome" % target2,target2)
                                                self.say("If you would like to apply for a server, please visit https://openredstone.org/apply/",target2)
                                                self.say("Please read the signs before proceeding to ask questions",target2)
                        for c in self.services:
                            self.say(".msg %s Welcome to ORE, %s! In order to get started, you can teleport to the welcome signs using /welcome" % (target2,target2),c)
                                                    self.say(".msg %s If you would like to apply for a server, please visit https://openredstone.org/apply/" % (target2),c)
                                                    self.say(".msg %s Please read the signs before proceeding to ask questions" % (target2),c)
                elif self.ctx["type"] == "PRIVMSG" and (self.nickname.lower() in self.ctx["msg"].lower()):
                    # something is speaking to the bot
                    query = self.ctx["msg"].lower().replace(self.nickname.lower(), "".join((self.bcolors["UNDERLINE"], self.nickname.lower(), self.bcolors["ENDC"])))
                    # do something intelligent here, like query a chatterbot
                    print ("someone spoke to us: ", query)
                    self.say("You called?", target)

                if self.ctx["sender"].split("!")[0]==self.nickname:
                    continue
                self.oldctx = {}
                self.oldctx["sender"]     = self.ctx["sender"]
                self.oldctx["sendername"] = self.ctx["sendername"]
                self.oldctx["type"]       = self.ctx["type"]
                self.oldctx["target"]     = self.ctx["target"]
                self.oldctx["msg"]         = self.ctx["msg"]

    def send(self, msg):
        print ("".join(("I> ",msg)))
        self.socket.send("".join((msg,"\r\n")).encode("latin1"))

    def getname(self):
        if any(x == self.ctx["sender"].split("!",1)[0] for x in self.services):
            name=self.ctx["msg"].split(":",1)[0]
        else:
            name=self.ctx["sendername"]
        return name

    def say(self, msg, to):
        if any(x == to for x in self.services):
            self.send("PRIVMSG %s :%s" % (to, ".msg %s %s" % (self.getname(), msg)))
        else:
            self.send("PRIVMSG %s :%s" % (to, msg))

    def perform(self):
        if self.password is not None:
            self.send("PASS %s" % self.password)
        if self.ident_password is not None:
            self.send("PRIVMSG nickserv : identify %s" % self.ident_password)
        for c in self.channels:
            self.send("JOIN %s" % c)

    def kick(self, c, victim, msg):
        self.send("KICK %s %s :%s" % (c, victim, msg))

    def isnumber(self, s):
        try:
            float(s)
            return True
        except TypeError:
            return False

    def calcexpression(self, expr):
        for kw in keyword.kwlist:
            if kw in expr:
                return None
        for word in dir():
            if word in expr:
                return None
        try:
            return eval(expr)
        except Exception as e:
            return e

config = {}
if os.path.isfile("./config.json"):
    with open("./config.json", "r") as f:
        config = json.load(f)
else:
    with open("./config.default.json", "r") as f:
        config = json.load(f)

client = IRCClient()
client.nickname = config["nickname"]
client.password = config["password"]
client.ident_password = config["ident_password"]
client.server = config["server"]
client.port = config["port"]
client.channels = {}
for chan in config["channels"]:
    client.channels[chan] = []
client.services = config["services"]
client.cmd = config["cmd"]

client.start()
