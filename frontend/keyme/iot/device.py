import sys
import os
from typing import Iterable

from awscrt import io, mqtt
from awsiot import mqtt_connection_builder


class Device:
    ENDPOINT = "a1gthlqk9w3ufv-ats.iot.ca-central-1.amazonaws.com"
    CLIENT_ID = "controller_dev"
    PATH_TO_CERTIFICATE = os.path.join(os.getcwd(),
                                       "certs",
                                       "041fe7d31e50e628c8aa5c6670753a39f873bcde8c966469c0c96a32ae3d5675-certificate.pem.crt")
    PATH_TO_PRIVATE_KEY = os.path.join(os.getcwd(),
                                       "certs",
                                       "041fe7d31e50e628c8aa5c6670753a39f873bcde8c966469c0c96a32ae3d5675-private.pem.key")
    PATH_TO_AMAZON_ROOT_CA_1 = os.path.join(os.getcwd(), "certs", "AmazonRootCA1.pem")
    TOPIC = "arduino/incoming"

    def __init__(self):
        event_loop_group = io.EventLoopGroup(1)
        host_resolver = io.DefaultHostResolver(event_loop_group)
        client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver)
        self.conn = mqtt_connection_builder.mtls_from_path(
            endpoint=self.ENDPOINT,
            cert_filepath=self.PATH_TO_CERTIFICATE,
            pri_key_filepath=self.PATH_TO_PRIVATE_KEY,
            client_bootstrap=client_bootstrap,
            ca_filepath=self.PATH_TO_AMAZON_ROOT_CA_1,
            client_id=self.CLIENT_ID,
            clean_session=False,
            keep_alive_secs=6
        )
        self.conn.connect().result()

    def publish(self, code: int, payload: Iterable[int]):
        data = bytearray()
        data.append(0x0F)
        data.append(code)
        data.extend(payload)

        self.conn.publish(topic=self.TOPIC, payload=data, qos=mqtt.QoS.AT_MOST_ONCE)
