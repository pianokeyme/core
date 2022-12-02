import sys
import mido
import shortuuid
import boto3
from midi2audio import FluidSynth
import pydub
from datetime import datetime

from keyme.pb import Analyzed
from keyme.s3 import Repository as S3Repository, Audio
from keyme.db import Repository as DbRepository, RecordingRow

NOTE_STR = ['c', 'c#', 'd', 'd#', 'e', 'f', 'f#', 'g', 'g#', 'a', 'a#', 'b']


def to_str(notes):
    notes_str = []

    for keys in notes:
        keys_str = []

        for i, key in enumerate(keys):
            note = key % 12
            octave = (key - 24) // 12
            keys_str.append(NOTE_STR[note] + str(octave))

        notes_str.append(keys_str)

    return notes_str


def to_analyzed_notes(notes):
    notes_analyzed = []

    for keys in notes:
        notes_analyzed.append(len(keys) * 2)

        for key in keys:
            note = key % 12
            octave = (key - 24) // 12
            notes_analyzed.append(note)
            notes_analyzed.append(octave)

    return notes_analyzed


def parse_midi(file) -> (list[int], float):
    curr = 0
    frame_size = 100 * 1000
    frame_index = 0

    notes = [[]]

    mid = mido.MidiFile(file)
    for msg in mid:
        curr += int(msg.time * 1e6)

        if msg.is_meta:
            continue

        if msg.type != "note_on" and msg.type != "note_off":
            continue

        index = curr // frame_size

        note = int(msg.note)
        on = msg.type == "note_on"

        if index - frame_index > 1:
            for i in range(index - frame_index - 1):
                notes.append(notes[len(notes) - 1].copy())

            frame_index = index - 1

        last = notes[len(notes) - 1].copy()

        if on:
            if note not in last:
                last.append(note)
        else:
            if note in last:
                last.remove(note)

        if index > frame_index:
            notes.append(last)
        else:
            notes[len(notes) - 1] = last

        frame_index = index

    return to_analyzed_notes(notes), float(frame_size / 1000)


def midi_to_mp3(in_file) -> str:
    wav_file = "output.wav"
    out_file = "output.mp3"

    fs = FluidSynth()
    fs.midi_to_audio(in_file, wav_file)

    pydub.AudioSegment.from_wav(wav_file).export(out_file, format="mp3", bitrate="128k")

    return out_file


def main():
    if len(sys.argv) < 3:
        sys.stderr.write("not enough arguments provided")
        sys.exit(1)

    db_repo = DbRepository()

    session = boto3.session.Session(profile_name="uottawa", region_name="ca-central-1")

    s3 = session.resource("s3")

    s3_repo = S3Repository(s3)

    file = sys.argv[1]
    name = sys.argv[2]

    mp3_file = midi_to_mp3(file)

    notes, frame_size = parse_midi(file)

    analyzed_id = shortuuid.uuid()

    analyzed = Analyzed()
    analyzed.version = 1
    analyzed.id = analyzed_id
    analyzed.frameSize = frame_size
    analyzed.notes.extend(notes)

    analyzed_ref = s3_repo.save_analyzed(analyzed)

    audio = Audio(analyzed_id)

    audio_ref = s3_repo.save_audio(mp3_file, audio)

    recording_row = RecordingRow(0, name, 0, 0, True, 1, datetime.now(), audio_ref, 1, analyzed_ref, 1)

    db_repo.save_recording(recording_row)


if __name__ == "__main__":
    main()
