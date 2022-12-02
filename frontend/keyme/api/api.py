import http
import time

import boto3
from flask import Flask, jsonify, request

from .models import Recording, RecordingSchema, Preferences, PreferencesSchema
from keyme.db import Repository as DbRepository, RecordingRow, PreferencesRow
from keyme.s3 import Repository as S3Repository
from keyme.iot import Device

sizes = {
    "Keyboard (61)": 61,
    "Grand (88)": 88,
}

schemes = {
    "Default": 0,
    "Rainbow": 1,
    "Gradient": 2,
}


def hex_to_rgb(c_hex: str) -> (int, int, int):
    c_hex = c_hex.removeprefix("#")
    rgb = int(c_hex, 16)
    r = (rgb >> 16) & 0xff
    g = (rgb >> 8) & 0xff
    b = rgb & 0xff
    return r, g, b


device = Device()

db_repo = DbRepository()

session = boto3.session.Session(profile_name="uottawa", region_name="ca-central-1")

s3 = session.resource("s3")

s3_repo = S3Repository(s3)

app = Flask(__name__)


def send_size(size):
    message = [size]
    device.publish(0x65, message)


def send_color(r, g, b):
    message = [r, g, b]
    device.publish(0x66, message)


def send_scheme(scheme):
    message = [scheme]
    device.publish(0x67, message)


def recording_from_row(row: RecordingRow):
    recording = Recording.from_db(row)
    recording.audio_url = s3_repo.audio_ref_to_url(row.audio_data_ref)
    return recording


@app.route("/api/recordings", methods=["GET"])
def get_recordings():
    schema = RecordingSchema(many=True)

    db_recordings = db_repo.get_all_recordings()
    recordings = map(recording_from_row, db_recordings)

    return jsonify(schema.dump(recordings))


@app.route("/api/recording/<int:recording_id>", methods=["DELETE"])
def remove_recording(recording_id: int):
    row = RecordingRow.from_id(recording_id)

    db_repo.remove_recording(row)

    return "", http.HTTPStatus.NO_CONTENT


@app.route("/api/preferences", methods=["PUT"])
def save_preferences():
    schema = PreferencesSchema()
    preferences: Preferences = schema.load(request.get_json())

    row = PreferencesRow(0, 0, schema.dumps(preferences))

    db_repo.save_preferences(row)

    size = sizes[preferences.size]
    scheme = schemes[preferences.scheme]
    r, g, b = hex_to_rgb(preferences.color)

    send_size(size)
    time.sleep(0.25)
    send_scheme(scheme)
    time.sleep(0.25)
    send_color(r, g, b)

    return "", http.HTTPStatus.NO_CONTENT
