from bson.codec_options import TypeCodec

from model.Position import Position


class PositionCodec(TypeCodec):
    python_type = Position
    bson_type = str

    def transform_python(self, value):
        return value.name

    def transform_bson(self, value):
        return Position(value)


# position_codec = PositionCodec()
