from keyme.pb import Analyzed

from .audio import Audio


class Repository:
    REGION = "ca-central-1"

    s3 = None
    bucket = None

    def __init__(self, s3):
        self.s3 = s3
        self.bucket = s3.Bucket("keyme-dev")

    @staticmethod
    def _ref_split(ref: str) -> (str, str):
        ref = ref.removeprefix("s3://")
        parts = ref.split("/", maxsplit=1)

        if len(parts) < 2:
            return "", ""

        return parts[0], parts[1]

    def save_audio(self, file, audio: Audio) -> str:
        name = audio.id + "/audio.mp3"

        self.bucket.upload_file(file, name, {"ContentType": "audio/mpeg"})

        return f"s3://{self.bucket.name}/{name}"

    def save_analyzed(self, analyzed: Analyzed) -> str:
        name = analyzed.id + "/analyzed.pb"

        body = analyzed.SerializeToString()

        self.bucket.put_object(Key=name, Body=body, ContentType="application/x-protobuf")

        return f"s3://{self.bucket.name}/{name}"

    def get_analyzed(self, ref: str) -> Analyzed | None:
        bucket, file = self._ref_split(ref)

        if not bucket:
            return None

        res = self.s3.Object(bucket, file).get()

        data = res['Body'].read()

        analyzed = Analyzed()
        analyzed.ParseFromString(data)

        return analyzed

    def audio_ref_to_url(self, ref: str) -> str:
        bucket, file = self._ref_split(ref)

        if not bucket:
            return ""

        return f"https://{bucket}.s3.{self.REGION}.amazonaws.com/{file}"
