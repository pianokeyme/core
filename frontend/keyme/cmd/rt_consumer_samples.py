import uuid
import logging

from confluent_kafka import Consumer

import config
from keyme.consumer.rt_samples import RTSamplesConsumer


def main():
    logging.basicConfig(level=logging.DEBUG)

    conf = {"bootstrap.servers": config.bootstrap_server,
            "group.id": "default:samples:rt",
            "client.id": uuid.uuid4(),
            "auto.offset.reset": config.auto_offset_reset}

    consumer = Consumer(conf)

    RTSamplesConsumer(consumer, config.topic_samples, config.temp_rt_dir).run()


if __name__ == "__main__":
    main()
