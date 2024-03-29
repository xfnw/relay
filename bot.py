#!/usr/bin/env python3

import asyncio, random

from irctokens import build, Line
from ircrobots import Bot as BaseBot
from ircrobots import Server as BaseServer
from ircrobots import ConnectionParams
# aaaaaaaaaaaaaAAAAAAAAAAAAAAA
# im too lazy to import more stuffs :tm:
from ircrobots.server import *

from config import *

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
            print(f"connected to {self.name}")
            self.chan = FNCHANNEL if self.name in ["freenode","libera"] else CHANNEL
            await self.send(build("JOIN", [self.chan]))
        if line.command == "PRIVMSG" and line.params.pop(0) == self.chan:
            text = line.params[0].replace("\1ACTION","*").replace("\1","")
            nick = line.source.split('!')[0]
            if nick == self.nickname or (line.tags and "batch" in line.tags) or "\x0f\x0f\x0f\x0f" in text:
                return
            if self.disconnected:
                return
            if nick.lower() in self.users and self.users[nick.lower()].account in ADMINS:
                if text[:len(self.nickname)+2].lower() == f'{self.nickname}: '.lower():
                    args = text[len(self.nickname)+2:].split(' ')
                    if args[0] == 'connect' and len(args) > 4:
                        await self.bot.add_server(args[1],ConnectionParams(NICKNAME,args[2],args[3],bool(int(args[4]))))
                        await self.send(build("PRIVMSG",[self.chan,"Connected to {} :3".format(args[1])]))
                        return
                    if args[0] == 'unlink' and len(args) > 1:
                        await self.bot.servers[args[1]].disconnect()
                        del self.bot.servers[args[1]]
                        await self.send(build("PRIVMSG",[self.chan,"Unlinked {} :S".format(args[1])]))
                        return
                    for i in random.sample(list(self.bot.servers),len(self.bot.servers)):
                        asyncio.create_task(self.bot.servers[i].ac(self.name,args))
                    return
            for npn in NOPING:
                offset = 1
                for loc in find_all_indexes(text.lower(), npn.lower()):
                    text = text[:loc+offset]+"\u200c"+text[loc+offset:]
                    offset += 1
            for i in random.sample(list(self.bot.servers),len(self.bot.servers)):
                asyncio.create_task(self.bot.servers[i].bc(self.name,nick,text))
            #await self.send(build("PRIVMSG ##xfnw :ine and boat ",[text]))
        if line.command == "INVITE":
            await self.send(build("JOIN",[line.params[1]]))
    async def line_send(self, line: Line):
        print(f"{self.name} > {line.format()}")
    async def bc(self,name,nick,msg):
        if self.disconnected or name == self.name or "chan" not in list(dir(self)):
            return
        await self.send(build("PRIVMSG",[self.chan,"\x0f\x0f\x0f\x0f<"+nick[:1]+"\u200c"+nick[1:]+"@"+name+"> "+msg]))
    async def ac(self,name,args):
        if self.disconnected  or "chan" not in list(dir(self)):
            return
        nargs = []
        isComb = False
        for arg in args:
            if arg[0] == ':':
                isComb = True
                nargs.append(arg[1:])
                continue
            if isComb:
                nargs[-1] += ' '+arg
            else:
                nargs.append(arg)
        await self.send(build(nargs[0],[self.chan]+nargs[1:]))

class Bot(BaseBot):
    def create_server(self, name: str):
        return Server(self, name)



def find_all_indexes(input_str, search_str):
    l1 = []
    length = len(input_str)
    index = 0
    while index < length:
        i = input_str.find(search_str, index)
        if i == -1:
            return l1
        l1.append(i)
        index = i + 1
    return l1



async def main():
    bot = Bot()
    for name, host, port, ssl in SERVERS:
        params = ConnectionParams(NICKNAME, host, port, ssl)
        await bot.add_server(name, params)

    await bot.run()

if __name__ == "__main__":
    asyncio.run(main())
