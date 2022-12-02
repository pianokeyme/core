from datetime import datetime
import os
import sys

from confluent_kafka import Consumer, KafkaError, KafkaException
import pydub
import numpy as np

from keyme.pb import Sample, Analyzed
from keyme.db import RecordingRow, Repository as DbRepository
from keyme.s3 import Audio, Repository as S3Repository


class RTEndConsumer:
    db_repo: DbRepository = None
    s3_repo: S3Repository = None
    consumer: Consumer = None
    topic: str = None
    input_dir: str = None
    output_dir: str = None

    def __init__(self, db_repo, s3_repo, consumer, topic, input_dir, output_dir):
        self.db_repo = db_repo
        self.s3_repo = s3_repo
        self.consumer = consumer
        self.topic = topic
        self.input_dir = input_dir
        self.output_dir = output_dir

    def handle_end(self, msg):
        rec_id = msg.key().decode("utf-8")

        in_folder = os.path.join(self.input_dir, rec_id)
        out_folder = os.path.join(self.output_dir, rec_id)

        sample_files = [f for f in os.listdir(in_folder) if f.endswith(".pb")]

        if len(sample_files) == 0:
            return

        sample_files.sort()

        sample_rate = -1.0
        frame_size = -1.0
        notes: list[int] = []
        init = False

        if not os.path.exists(out_folder):
            os.makedirs(out_folder)

        with open(os.path.join(out_folder, "audio.bin"), "w+b") as audio_file:
            for file in sample_files:
                with open(os.path.join(in_folder, file), "rb") as f:
                    data = f.read()

                sample = Sample()
                sample.ParseFromString(data)

                if not init:
                    sample_rate = sample.sampleRate
                    frame_size = sample.frameSize

                notes.append(len(sample.notes))
                if len(sample.notes) > 0:
                    notes.extend([int(note) for note in sample.notes])

                samples = np.asarray(sample.samples, "float32")

                audio_file.write(samples.tobytes())

        audio: np.ndarray = np.fromfile(os.path.join(out_folder, "audio.bin"), dtype="float32")

        audio = np.nan_to_num(audio, copy=False)
        audio /= np.linalg.norm(audio, np.inf)
        audio *= (2 ** 31)

        audio_raw = audio.astype(np.int32)

        audio_segment = pydub.AudioSegment(audio_raw.tobytes(), sample_width=4, channels=1, frame_rate=int(sample_rate))

        file = os.path.join(out_folder, "audio.mp3")

        audio_segment.export(file, format="mp3", bitrate="128k")

        s3_audio = Audio(rec_id)

        audio_ref = self.s3_repo.save_audio(file, s3_audio)

        analyzed = Analyzed()
        analyzed.version = 1
        analyzed.id = rec_id
        analyzed.frameSize = frame_size
        analyzed.notes.extend(notes)

        analyzed_ref = self.s3_repo.save_analyzed(analyzed)

        recording_row = RecordingRow(0, "", 0, 0, False, 1, datetime.now(), audio_ref, 1, analyzed_ref, 1)

        self.db_repo.save_recording(recording_row)

        print(f"end: processed {rec_id}")

    def poll(self):
        msg = self.consumer.poll(timeout=0.25)

        if msg is None:
            return

        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                # End of partition event
                sys.stderr.write('%% %s [%d] reached end at offset %d\n' %
                                 (msg.topic(), msg.partition(), msg.offset()))
            elif msg.error():
                raise KafkaException(msg.error())
        else:
            self.handle_end(msg)

    def poll_loop(self):
        while True:
            self.poll()

    def run(self):
        self.consumer.subscribe([self.topic])

        print(f"end: consuming messages from {self.topic}")

        try:
            self.poll_loop()
        finally:
            self.consumer.close()
