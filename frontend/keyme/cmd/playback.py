import time

from keyme.pb import Analyzed
from keyme.iot import Device


class Playback:
    NOTE_STR = ['c', 'c#', 'd', 'd#', 'e', 'f', 'f#', 'g', 'g#', 'a', 'a#', 'b']

    def __init__(self, device: Device, analyzed: Analyzed, size: int):
        self.device = device
        self.analyzed = analyzed
        self.i = 0
        self.rate = 1.0
        self.size = size
        self.paused = True
        self.done = False
        self.prev_message = []

        if self.size == 88:
            self.NOTE_OFFSET = 0 * 12 + 9  # startingOctave * 12 + startingNote
        else:
            self.NOTE_OFFSET = 2 * 12 + 0  # startingOctave * 12 + startingNote

    def play(self, rate):
        if self.done:
            return

        if rate > 0:
            self.rate = rate
        else:
            self.rate = 1.0

        self.paused = False

    def pause(self):
        if self.done:
            return

        self.paused = True

    def finish(self):
        message = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        self.device.publish(0x64, message)

        self.done = True

    def run(self):
        if self.done:
            return

        if len(self.analyzed.notes) == 0 or self.analyzed.frameSize == 0.0:
            return

        n = len(self.analyzed.notes)
        delay = self.analyzed.frameSize / 1000.0

        while True:
            if self.done:
                return

            if self.paused:
                time.sleep(1 / 1000)
                continue

            if self.i >= n:
                break

            num = int(self.analyzed.notes[self.i])

            if self.i + num >= n or num % 2 != 0:
                break

            message = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]

            if num == 0:
                print("-")
            else:
                a = ""

                for j in range(num // 2):
                    note = self.analyzed.notes[self.i + (j * 2) + 1]
                    octave = self.analyzed.notes[self.i + (j * 2) + 2]
                    index = (octave * 12 + note) - self.NOTE_OFFSET

                    if index >= 0 and int(index) < len(message) * 8:
                        message[index // 8] |= 0b10000000 >> (index % 8)

                    if j != 0:
                        a += ", "
                    a += self.NOTE_STR[note] + str(octave)

                print(a)

            self.i += num + 1

            if message != self.prev_message:
                self.device.publish(0x64, message)

            self.prev_message = message

            time.sleep(delay / self.rate)

        self.done = True
