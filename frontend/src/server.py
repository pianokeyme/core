import asyncio
import json
import math
import os

import numpy
import websockets
import numpy as np
from scipy import signal, fft
from awscrt import io, mqtt
from awsiot import mqtt_connection_builder

ENDPOINT = "a1gthlqk9w3ufv-ats.iot.ca-central-1.amazonaws.com"
CLIENT_ID = "controller_dev"
PATH_TO_CERTIFICATE = "certs/041fe7d31e50e628c8aa5c6670753a39f873bcde8c966469c0c96a32ae3d5675-certificate.pem.crt"
PATH_TO_PRIVATE_KEY = "certs/041fe7d31e50e628c8aa5c6670753a39f873bcde8c966469c0c96a32ae3d5675-private.pem.key"
PATH_TO_AMAZON_ROOT_CA_1 = "certs/AmazonRootCA1.pem"
TOPIC = "arduino/incoming"

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


class Client:
    NOTE_STRING = ['C', 'C#/Db', 'D', 'D#/Eb', 'E', 'F', 'F#/Gb', 'G', 'G#/Ab', 'A', 'A#/Bb', 'B']
    THRESHOLD = 0.001
    NOTE_OFFSET = 0 * 12 + 9  # starting octave = 0, starting note = 9 (A)

    def __init__(self, websocket):
        self.websocket = websocket
        self.init = False
        self.sampleRate = -1
        self.frameSize = -1  # length of frame in ms

    def bandpass_filter(self, raw_signal):
        numerator, denominator = signal.butter(5, [15, 8000], 'bandpass',
                                               fs=self.sampleRate)  # order 5 keep frequencies between 15hz and 8000hz. Diff not visiable
        filtered = signal.lfilter(numerator, denominator, raw_signal)
        return filtered

    def generate_freq_spectrum(self, x):
        """
        Derive frequency spectrum of a signal from time domain
        :param x: signal in the time domain
        :param sf: sampling frequency
        :returns frequencies and their content distribution
        """
        x = x - np.average(x)  # zero-centering

        n = len(x)
        k = np.arange(n)
        tarr = n / float(self.sampleRate)  ####num of sample
        frqarr = k / float(tarr)  # two sides frequency range

        frqarr = frqarr[range(n // 2)]  # one side frequency range

        x = fft.fft(x) / n  # fft computing and normalization
        x = x[range(n // 2)]

        return frqarr, abs(x)

    def frequency_to_note(self, frequency):
        log_peak_freq = math.log(frequency, 2)
        index = round((log_peak_freq - 3.94802101634847) / 0.0833334184464846)
        octave_num, note = index // 12, int(index % 12 - 1)
        return note, octave_num

    async def run(self):
        async for message in self.websocket:
            if not self.init:
                setup = json.loads(message)
                self.sampleRate = setup["sampleRate"]
                self.frameSize = setup["frameSize"] * 1000
                self.init = True
                print(f"new client, sampleRate={self.sampleRate}, frameSize={self.frameSize}")
                continue

            data = np.frombuffer(message, "float32")

            to_write = []

            for i in range(0, len(data)):
                to_write.append(f"{data[i]}")

            with open("./data.txt", "ab") as file:
                file.write(("\n".join(to_write) + "\n").encode("utf-8"))

            filtered_signal = self.bandpass_filter(data)
            frequency, signal_amplitude = self.generate_freq_spectrum(filtered_signal)  # fft
            peak_frequency_index = np.argmax(
                signal_amplitude)  # get peak freq, return the index of the highest value

            if signal_amplitude[peak_frequency_index] > self.THRESHOLD:
                note, octave = self.frequency_to_note(frequency[peak_frequency_index])
                index = (octave * 12 + note) - self.NOTE_OFFSET

                message = [0x0F, 0x64, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
                message[(index // 8) + 2] = 0b10000000 >> (index % 8)

                mqtt_connection.publish(topic=TOPIC, payload=bytes(message), qos=mqtt.QoS.AT_MOST_ONCE)

                print(f"{self.NOTE_STRING[note]}{octave} note={note} octave={octave} index={index}")


async def handler(websocket):
    await Client(websocket).run()


async def main():
    host = "0.0.0.0"
    port = 8001
    async with websockets.serve(handler, host, port):
        print(f"Server listening on {host}:{port}")
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
