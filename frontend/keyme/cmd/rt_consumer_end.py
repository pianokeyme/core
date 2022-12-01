import uuid
import logging

from confluent_kafka import Consumer
import boto3

import config
from keyme.consumer.rt_end import RTEndConsumer
from keyme.db.repository import Repository as DbRepository
from keyme.s3.repository import Repository as S3Repository


def main():
    logging.basicConfig(level=logging.DEBUG)

    conf = {"bootstrap.servers": config.bootstrap_server,
            "group.id": "default:samples:end",
            "client.id": uuid.uuid4(),
            "auto.offset.reset": config.auto_offset_reset}

    consumer = Consumer(conf)

    db_repo = DbRepository()

    session = boto3.session.Session(profile_name="uottawa", region_name="ca-central-1")

    s3 = session.resource("s3")

    s3_repo = S3Repository(s3)

    RTEndConsumer(db_repo, s3_repo, consumer, config.topic_end, config.temp_rt_dir, config.temp_end_dir).run()


if __name__ == "__main__":
    main()
