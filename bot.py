#!/usr/bin/env python3

import asyncio

from irctokens import build, Line
from ircrobots import Bot as BaseBot
from ircrobots import Server as BaseServer
from ircrobots import ConnectionParams

SERVERS = [
    ("freenode", "chat.freenode.net"),
    ("tilde", "irc.tilde.chat"),
    ("technet","irc.technet.xi.ht"),
    ("vulpineawoo","irc.wppnx.pii.at"),
    ("alphachat","irc.alphachat.net"),
]

class Server(BaseServer):
    async def line_read(self, line: Line):
        print(f"{self.name} < {line.format()}")
        if line.command == "001":
            print(f"connected to {self.isupport.network}")
            self.chan = "##xfnw" if self.name == "freenode" else "#xfnw"
            await self.send(build("JOIN", [self.chan]))
        if line.command == "PRIVMSG" and line.params.pop(0) == self.chan:
            text = line.params[0].replace("\1ACTION","*").replace("\1","")
            nick = line.source.split('!')[0]
            if nick == self.nickname or line.tags and "batch" in line.tags:
                return
            for i in self.bot.servers:
                asyncio.create_task(self.bot.servers[i].bc(self.name,nick,text))
            #await self.send(build("PRIVMSG ##xfnw :ine and boat ",[text]))
        if line.command == "INVITE":
            await self.send(build("JOIN",[line.params[1]]))
    async def line_send(self, line: Line):
        print(f"{self.name} > {line.format()}")
    async def bc(self,name,nick,msg):
        if name == self.name:
            return
        await self.send(build("PRIVMSG",[self.chan,"<"+nick+"@"+name+"> "+msg]))

class Bot(BaseBot):
    def create_server(self, name: str):
        return Server(self, name)

bot = 0
async def main():
    bot = Bot()
    for name, host in SERVERS:
        params = ConnectionParams("xfnwRelay", host, 6697, True)
        await bot.add_server(name, params)

    await bot.run()

if __name__ == "__main__":
    asyncio.run(main())
