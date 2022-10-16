import asyncio
import json

import websockets
import pandas as pd
import numpy as np

SAMPLE_RATE = 48000
FRAME_SIZE = 500 / 1000

df = pd.read_csv("../data.txt", dtype="float64")
arr: np.ndarray = df.to_numpy().reshape(len(df), )


async def main():
    async with websockets.connect("ws://localhost:8001") as websocket:
        await websocket.send(json.dumps({"sampleRate": SAMPLE_RATE, "frameSize": FRAME_SIZE}))

        i = 0
        j = int(SAMPLE_RATE * FRAME_SIZE)

        while j < len(arr):
            data: bytes = arr[i:j].tobytes()
            i = j
            j += int(SAMPLE_RATE * FRAME_SIZE)
            await websocket.send(data)
            print(f"{i}:{j}")
            await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
