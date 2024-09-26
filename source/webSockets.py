#! /usr/bin/env python3

import sys, json
import asyncio
from websockets import connect
import ssl

ssl_context = ssl._create_unverified_context()

class WebSocket:

    async def __aenter__(self):
        self._conn = connect(f"wss://127.0.0.1:5000/v1/api/ws", ssl=ssl_context)
        self.socket = await self._conn.__aenter__()
        return self

    async def __aexit__(self, *args, **kwargs):
        await self._conn.__aexit__(*args, **kwargs)

    async def send(self, message):
        await self.socket.send(message)

    async def receive(self):
        return await self.socket.recv()

class testSocket:

    def __init__(self):
        self.cpSocket = WebSocket()
        self.loop = asyncio.get_event_loop()

    def getHistoricalData(self):
        return self.loop.run_until_complete(self.__async__get_history())

    def testStream(self):
        return self.loop.run_until_complete(self.__async__testStream())

    async def __async__testStream(self):
        async with self.cpSocket as testConn:
            while True:
                rst = await testConn.receive()
                print(rst)

    async def __async__get_history(self):
        payload = "smh+265598+" + json.dumps(
                {
                    "period": "1d",
                    "bar": "5mins",
                    "source": "trades",
                    "format": "%o%h%c%l%v"
                    }
                )
        async with self.cpSocket as echo:
            await echo.send(payload)
            while True:
                rst = await echo.receive()
                print(rst)
#            return await echo.receive()

def main():

    socket = testSocket()
    response = socket.getHistoricalData()
    print(response)

if __name__ == "__main__":
    main()
