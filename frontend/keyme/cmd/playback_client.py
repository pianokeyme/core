import asyncio
import json
import time

import websockets


async def send(websocket, code, buf):
    data = bytearray()
    data.append(code)

    if isinstance(buf, str):
        data.extend(bytes(buf, "utf8"))
    else:
        data.extend(buf)

    await websocket.send(data)


async def main():
    async with websockets.connect("ws://localhost:8002") as websocket:
        await send(websocket, 100, json.dumps({"recordingId": 1000033}))
        await asyncio.sleep(1)
        await send(websocket, 101, json.dumps({"rate": 0.75}))
        await asyncio.sleep(5)
        await send(websocket, 102, "{}")
        await asyncio.sleep(5)
        await send(websocket, 101, json.dumps({"rate": 0.5}))
        await asyncio.sleep(5)
        await send(websocket, 103, "{}")


if __name__ == "__main__":
    asyncio.run(main())
