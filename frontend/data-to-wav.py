import pandas as pd
from scipy import signal
from scipy.io import wavfile


def bandpass_filter(raw_signal, fs):
    # order 5 keep frequencies between 15hz and 8000hz. Diff not visiable
    numerator, denominator = signal.butter(5, [15, 8000], 'bandpass',
                                           fs=fs)
    filtered = signal.lfilter(numerator, denominator, raw_signal)
    return filtered


def main():
    df = pd.read_csv("data.txt", dtype="float32")
    print(len(df))
    df = df.to_numpy().reshape(len(df), )
    print(df.shape)
    frame_size = 100  # length of each section in ms
    magnitude_threshold = 0
    frame_rate = 48000
    wavfile.write("./unfiltered.wav", frame_rate, df)
    filtered_signal = bandpass_filter(df, frame_rate)
    wavfile.write("./filtered.wav", frame_rate, filtered_signal)


if __name__ == "__main__":
    main()
