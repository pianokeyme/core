import asyncio

from keyme.pb import Analyzed
from keyme.iot import Device


class Playback:
    NOTE_STR = ['c', 'c#', 'd', 'd#', 'e', 'f', 'f#', 'g', 'g#', 'a', 'a#', 'b']
    NOTE_OFFSET = 2 * 12 + 0

    def __init__(self, device: Device, analyzed: Analyzed):
        self.device = device
        self.analyzed = analyzed
        self.i = 0
        self.paused = False
        self.done = False

    async def play(self):
        if self.done:
            return

        self.paused = False

        if len(self.analyzed.notes) == 0 or self.analyzed.frameSize == 0.0:
            return

        n = len(self.analyzed.notes)
        delay = self.analyzed.frameSize / 1000.0

        while True:
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

                    message[index // 8] = 0b10000000 >> (index % 8)

                    if j != 0:
                        a += ", "
                    a += self.NOTE_STR[note] + str(octave)

                print(a)

            self.i += num + 1

            self.device.publish(0x64, message)

            future = asyncio.Future()
            future.cancel()

            await asyncio.sleep(delay)

        self.done = True

    def pause(self):
        if self.done:
            return

        self.paused = True
