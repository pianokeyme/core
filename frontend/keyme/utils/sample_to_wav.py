import numpy as np
from scipy.io import wavfile
from keyme.pb import sample_pb2


def sample_to_wav(sample):
    samples = np.asarray(sample.samples, "float32")

    wavfile.write("./audio.wav", int(sample.sampleRate), samples)


def sample_file_to_wav(name):
    with open(name, "rb") as f:
        data = f.read()

    sample = sample_pb2.Sample()
    sample.ParseFromString(data)

    sample_to_wav(sample)
