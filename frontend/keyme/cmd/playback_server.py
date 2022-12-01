import asyncio
import logging
import json
import websockets

from keyme.db import Repository as DbRepository, RecordingRow
from keyme.s3 import Repository as S3Repository
from keyme.pb import Analyzed

import playback
import config


class PlaybackServer:
    MESSAGE_INIT = 100
    MESSAGE_START = 101
    MESSAGE_PAUSE = 102
    MESSAGE_END = 102

    db_repo: DbRepository = None
    s3_repo: S3Repository = None
    recording: RecordingRow = None
    analyzed: Analyzed = None

    def __init__(self, websocket, db_repo, s3_repo):
        self.playback = playback.Playback()
        self.websocket = websocket
        self.db_repo = db_repo
        self.s3_repo = s3_repo

    def handle_init(self, message):
        setup = json.loads(message[1:])

        rec_id = setup["recordingId"]

        recording = self.db_repo.get_recording(rec_id)

        if recording is None:
            return

        analyzed = self.s3_repo.get_analyzed(recording.analyzed_data_ref)

        if analyzed is None:
            return

        self.recording = recording
        self.analyzed = analyzed

    def handle_start(self, message):
        pass

    def handle_pause(self, message):
        pass

    def handle_end(self, message):
        pass

    async def handle_loop(self):
        async for message in self.websocket:
            message_id = int(message[0])

            if message_id == self.MESSAGE_INIT:
                self.handle_init(message)
            elif message_id == self.MESSAGE_START:
                self.handle_start(message)
            elif message_id == self.MESSAGE_PAUSE:
                self.handle_pause(message)
            elif message_id == self.MESSAGE_END:
                self.handle_end(message)
            else:
                print(f"playback: invalid message with id {message_id}")

    async def run(self):
        await self.handle_loop()


async def handler(websocket):
    server = PlaybackServer(websocket)
    await server.run()


async def main():
    logging.basicConfig(level=logging.DEBUG)

    async with websockets.serve(handler, config.playback_server_host, config.playback_server_port):
        print(f"Playback server listening on {config.playback_server_host}:{config.playback_server_port}")
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
