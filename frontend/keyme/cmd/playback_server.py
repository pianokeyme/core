import asyncio
import logging
import json
import websockets
import boto3
import threading

from keyme.db import Repository as DbRepository, RecordingRow
from keyme.s3 import Repository as S3Repository
from keyme.pb import Analyzed
from keyme.iot import Device

from playback import Playback
import config


class PlaybackServer:
    SIZES = {
        "Keyboard (61)": 61,
        "Grand (88)": 88,
    }

    MESSAGE_INIT = 100
    MESSAGE_START = 101
    MESSAGE_PAUSE = 102
    MESSAGE_END = 103

    db_repo: DbRepository = None
    s3_repo: S3Repository = None
    recording: RecordingRow = None
    analyzed: Analyzed = None
    playback: Playback = None

    def __init__(self, websocket, db_repo, s3_repo):
        self.device = Device()
        self.websocket = websocket
        self.db_repo = db_repo
        self.s3_repo = s3_repo
        self.size = 61

    def handle_init(self, message):
        setup = json.loads(message[1:])

        rec_id = setup["recordingId"]

        recording = self.db_repo.get_recording(rec_id)

        if recording is None:
            return

        analyzed = self.s3_repo.get_analyzed(recording.analyzed_data_ref)

        if analyzed is None:
            return

        prefs = self.db_repo.get_preferences(1)

        if prefs is None:
            return

        if self.playback:
            self.playback.finish()

        self.recording = recording
        self.analyzed = analyzed
        self.size = self.SIZES[json.loads(prefs.prefs)["size"]]
        self.playback = Playback(self.device, self.analyzed, self.size)
        self.thread = threading.Thread(target=self.playback.run)
        self.thread.daemon = True
        self.thread.start()

    def handle_start(self, message):
        conf = json.loads(message[1:])
        rate = conf["rate"]

        self.playback.play(rate)

    def handle_pause(self, message):
        self.playback.pause()

    def handle_end(self, message):
        self.playback.finish()

    async def handle_loop(self):
        async for message in self.websocket:
            message_id = int(message[0])

            print("message", message_id)

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


async def main():
    logging.basicConfig(level=logging.DEBUG)

    db_repo = DbRepository()

    session = boto3.session.Session(profile_name="uottawa", region_name="ca-central-1")

    s3 = session.resource("s3")

    s3_repo = S3Repository(s3)

    async def handler(websocket):
        server = PlaybackServer(websocket, db_repo, s3_repo)
        await server.run()

    async with websockets.serve(handler, config.playback_server_host, config.playback_server_port):
        print(f"Playback server listening on {config.playback_server_host}:{config.playback_server_port}")
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
