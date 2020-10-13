#!/usr/bin/env python3

import asyncio

from irctokens import build, Line
from ircrobots import Bot as BaseBot
from ircrobots import Server as BaseServer
from ircrobots import ConnectionParams
# aaaaaaaaaaaaaAAAAAAAAAAAAAAA
# im too lazy to import more stuffs :tm:
from ircrobots.server import *

SERVERS = [
    ("freenode", "chat.freenode.net", 6697, True),
    ("tilde", "irc.tilde.chat", 6697, True),
    ("technet","irc.technet.xi.ht", 6697, True),
    ("vulpineawoo","irc.wppnx.pii.at", 6697, True),
    ("alphachat","irc.alphachat.net", 6697, True),
    ("openirc","91.188.125.227",6668,False),
]

class Server(BaseServer):

    # overwrite connect so i can put try except blocks there
    async def connect(self,
            transport: ITCPTransport,
            params: ConnectionParams):
        try:
            await sts_transmute(params)
            await resume_transmute(params)

            reader, writer = await transport.connect(
                params.host,
                params.port,
                tls       =params.tls,
                tls_verify=params.tls_verify,
                bindhost  =params.bindhost)

            self._reader = reader
            self._writer = writer

            self.params = params
            await self.handshake()
        except:
            print('connection with {} failed, disconnecting'.format(self.name))
            self.disconnected = True

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
        if self.disconnected or name == self.name or "chan" not in list(dir(self)):
            return
        await self.send(build("PRIVMSG",[self.chan,"<"+nick+"@"+name+"> "+msg]))

class Bot(BaseBot):
    def create_server(self, name: str):
        return Server(self, name)

bot = 0
async def main():
    bot = Bot()
    for name, host, port, ssl in SERVERS:
        params = ConnectionParams("xfnwRelay", host, port, ssl)
        await bot.add_server(name, params)

    await bot.run()

if __name__ == "__main__":
    asyncio.run(main())
