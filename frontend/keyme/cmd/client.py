import asyncio
import json
import math
import time

import websockets
import pandas as pd
import numpy as np

SAMPLE_RATE = 48000
FRAME_SIZE = 500 / 1000


async def send(websocket, code, buf):
    data = bytearray()
    data.append(code)

    if isinstance(buf, str):
        data.extend(bytes(buf, "utf8"))
    else:
        data.extend(buf)

    await websocket.send(data)


async def main():
    df = pd.read_csv("../../testdata/data.txt", dtype="float32")
    arr: np.ndarray = df.to_numpy().reshape(len(df), )[:int(SAMPLE_RATE * 60)]
    n = math.floor(len(arr) / (SAMPLE_RATE * FRAME_SIZE)) * int(SAMPLE_RATE * FRAME_SIZE)

    async with websockets.connect("ws://localhost:8001") as websocket:
        await send(websocket, 100, json.dumps({"sampleRate": SAMPLE_RATE, "frameSize": FRAME_SIZE}))

        i = 0
        j = int(SAMPLE_RATE * FRAME_SIZE)

        while j <= len(arr):
            if i > 0:
                await asyncio.sleep(0.25)

            data: bytes = arr[i:j].tobytes()

            print(f"{i}:{j} {math.ceil((j / n) * 100)}% time={int(time.time_ns() / 1e6)}")

            i = j
            j += int(SAMPLE_RATE * FRAME_SIZE)

            await send(websocket, 101, data)

        await send(websocket, 102, "{}")


if __name__ == "__main__":
    asyncio.run(main())
