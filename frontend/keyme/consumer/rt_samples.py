import sys
import os
import time
from confluent_kafka import Consumer, KafkaError, KafkaException

from keyme.pb import Sample


class RTSamplesConsumer:
    consumer: Consumer = None
    topic: str = None
    output_dir: str = None

    def __init__(self, consumer, topic, output_dir):
        self.consumer = consumer
        self.topic = topic
        self.output_dir = output_dir

    def handle_sample(self, msg):
        sample = Sample()
        sample.ParseFromString(msg.value())

        folder = os.path.join(self.output_dir, sample.id)
        name = str(sample.seq).rjust(10, "0") + ".pb"

        if not os.path.exists(folder):
            os.makedirs(folder)

        with open(os.path.join(folder, name), "w+b") as f:
            f.write(msg.value())

        print(f"id={sample.id} len={len(msg) // 1024}kb time={int(time.time_ns() / 1e6)}")

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
            self.handle_sample(msg)

    def poll_loop(self):
        while True:
            self.poll()

    def run(self):
        self.consumer.subscribe([self.topic])

        print(f"rt: consuming messages from {self.topic}")

        try:
            self.poll_loop()
        finally:
            self.consumer.close()
