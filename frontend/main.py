import asyncio
import random
import time

from awscrt import io, mqtt, auth, http
from awsiot import mqtt_connection_builder
import time as t
import json

# Define ENDPOINT, CLIENT_ID, PATH_TO_CERTIFICATE, PATH_TO_PRIVATE_KEY, PATH_TO_AMAZON_ROOT_CA_1, MESSAGE, TOPIC, and RANGE
ENDPOINT = "a1gthlqk9w3ufv-ats.iot.ca-central-1.amazonaws.com"
CLIENT_ID = "controller_dev"
PATH_TO_CERTIFICATE = "certs/041fe7d31e50e628c8aa5c6670753a39f873bcde8c966469c0c96a32ae3d5675-certificate.pem.crt"
PATH_TO_PRIVATE_KEY = "certs/041fe7d31e50e628c8aa5c6670753a39f873bcde8c966469c0c96a32ae3d5675-private.pem.key"
PATH_TO_AMAZON_ROOT_CA_1 = "certs/AmazonRootCA1.pem"
MESSAGE = "Hello World 3"
RANGE = 1

TOPIC = "arduino/incoming"


def on_message_received(topic, payload, dup, qos, retain, **kwargs):
    print("Received message from topic '{}': {}".format(topic, payload))


# Spin up resources
event_loop_group = io.EventLoopGroup(1)
host_resolver = io.DefaultHostResolver(event_loop_group)
client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver)
mqtt_connection = mqtt_connection_builder.mtls_from_path(
    endpoint=ENDPOINT,
    cert_filepath=PATH_TO_CERTIFICATE,
    pri_key_filepath=PATH_TO_PRIVATE_KEY,
    client_bootstrap=client_bootstrap,
    ca_filepath=PATH_TO_AMAZON_ROOT_CA_1,
    client_id=CLIENT_ID,
    clean_session=False,
    keep_alive_secs=6
)
print("Connecting to {} with client ID '{}'...".format(
    ENDPOINT, CLIENT_ID))
# Make the connect() call
connect_future = mqtt_connection.connect()
# Future.result() waits until a result is available
connect_future.result()
print("Connected!")
# Publish message to server desired number of times.

# print("Begin Subscribe")
# mqtt_connection.subscribe(topic=TOPIC, qos=mqtt.QoS.AT_LEAST_ONCE, callback=on_message_received)

print('Begin Publish')
for i in range(RANGE):
    # message = "{} [{}]".format(MESSAGE, i + 1)
    # message = [0x0F, 0x64, 0x55, 0x55, 0x55, 0x55, 0x55, 0x55, 0x55, 0x55, 0x55, 0x55, 0x55]
    message = [0x0F, 0x64, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]

    note = 0
    octave = 4

    index = (octave * 12 + note) - (0 * 12 + 9)
    message[(index // 8) + 2] = 0b10000000 >> (index % 8)

    # message = [0x0F, 0x64]
    #
    # for j in range(11):
    #     message.append(random.randint(0, 255))

    data = bytes(message)

    ms = time.time_ns() // 1_000_000

    mqtt_connection.publish(topic=TOPIC, payload=data, qos=mqtt.QoS.AT_MOST_ONCE)
    print("Published to {}: ({}) {} {}ms".format(TOPIC, len(data), data, ms))
    t.sleep(1)
print('Publish End')

disconnect_future = mqtt_connection.disconnect()
disconnect_future.result()
