import asyncio
import json
import sys
import uuid
import logging

import websockets
import numpy as np
import shortuuid
from confluent_kafka import Producer

from keyme.dsp import Analyzer
from keyme.pb import Sample
from keyme.iot import Device
from keyme.db import Repository as DbRepository, PreferencesRow
import config


class RTServer:
    SIZES = {
        "Keyboard (61)": 61,
        "Grand (88)": 88,
    }

    NOTE_STRING = ['C', 'C#/Db', 'D', 'D#/Eb', 'E', 'F', 'F#/Gb', 'G', 'G#/Ab', 'A', 'A#/Bb', 'B']
    THRESHOLD = 5000

    MESSAGE_START = 100
    MESSAGE_SAMPLE = 101
    MESSAGE_END = 102

    def __init__(self, websocket, db_repo: DbRepository, producer: Producer, topic_samples: str, topic_end: str):
        self.device = Device()
        self.websocket = websocket
        self.db_repo = db_repo
        self.analyzer = None
        self.producer = producer
        self.topic_samples = topic_samples
        self.topic_end = topic_end
        self.init = False
        self.sampleRate = -1
        self.frameSize = -1  # length of frame in ms
        self.id = ""
        self.seq = -1
        self.prefs = PreferencesRow(0, 0, "")

    def analyzed_to_index(self, note: str, octave: str) -> (int, int, int):
        if not note or not octave:
            return -1, -1, -1

        try:
            octave_n = int(octave)
        except ValueError:
            return -1, -1, -1

        note_n = -1
        i = 0

        for note_str in self.NOTE_STRING:
            if note_str == note:
                note_n = i
                break
            i += 1

        if note_n == -1:
            return -1, -1, -1

        return (octave_n * 12 + note_n) - self.NOTE_OFFSET, note_n, octave_n

    def handle_sample(self, message):
        if not self.init:
            sys.stderr.write("websocket: received sample message before init\n")
            return

        samples = np.frombuffer(message, dtype="float32", offset=1)

        sample = Sample()
        sample.version = 1
        sample.id = self.id
        sample.seq = self.seq
        sample.sampleRate = self.sampleRate
        sample.frameSize = self.frameSize
        sample.samples.extend(samples)

        audio = np.nan_to_num(samples)
        audio /= np.linalg.norm(audio, np.inf)
        audio *= (2 ** 15)

        audio_raw = audio.astype(np.int16)

        note, octave = self.analyzer.analysis(audio_raw)
        index, note_n, octave_n = self.analyzed_to_index(note, octave)

        notes = []

        if index != -1:
            notes.extend([note_n, octave_n])

            message = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
            message[index // 8] |= 0b10000000 >> (index % 8)

            self.device.publish(0x64, message)

            print(f"{self.NOTE_STRING[note_n]}{octave_n} note={note} octave={octave} index={index}")

        sample.notes.extend(notes)

        data = sample.SerializeToString()
        self.producer.produce(self.topic_samples, key=self.id, value=data)

        self.seq += 1

    def handle_start(self, message):
        setup = json.loads(message[1:])

        self.sampleRate = setup["sampleRate"]
        self.frameSize = setup["frameSize"] * 1000
        self.id = shortuuid.uuid()
        self.seq = 1
        self.analyzer = Analyzer(self.THRESHOLD, self.sampleRate)
        self.init = True

        print(f"rt: {self.id} start, sampleRate={self.sampleRate}, frameSize={self.frameSize}")

    def handle_end(self, message):
        if not self.init:
            sys.stderr.write("websocket: received end message before init\n")
            return

        self.producer.flush()
        self.producer.produce(self.topic_end, key=self.id, value=self.id)

        print(f"rt: {self.id} end")

        self.sampleRate = -1
        self.frameSize = -1
        self.id = ""
        self.seq = -1
        self.init = False

    async def handle_loop(self):
        async for message in self.websocket:
            message_id = int(message[0])

            if message_id == self.MESSAGE_START:
                self.handle_start(message)
            elif message_id == self.MESSAGE_END:
                self.handle_end(message)
            elif message_id == self.MESSAGE_SAMPLE:
                self.handle_sample(message)
            else:
                print(f"rt: invalid message with id {message_id}")

    async def run(self):
        prefs = self.db_repo.get_preferences(1)

        if prefs is None:
            return

        self.size = self.SIZES[json.loads(prefs.prefs)["size"]]

        if self.size == 88:
            self.NOTE_OFFSET = 0 * 12 + 9  # startingOctave * 12 + startingNote
        else:
            self.NOTE_OFFSET = 2 * 12 + 0  # startingOctave * 12 + startingNote

        try:
            await self.handle_loop()
        finally:
            self.producer.flush()


async def main():
    logging.basicConfig(level=logging.DEBUG)

    conf = {'bootstrap.servers': config.bootstrap_server,
            'client.id': uuid.uuid4()}

    producer = Producer(conf)

    db_repo = DbRepository()

    async def handler(websocket):
        server = RTServer(websocket, db_repo, producer, config.topic_samples, config.topic_end)
        await server.run()

    async with websockets.serve(handler, config.server_host, config.server_port):
        print(f"Server listening on {config.server_host}:{config.server_port}")
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
