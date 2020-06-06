import base64
from marshmallow import Schema, fields


class CommandSchema(Schema):
    """
    Simple key/value type commands.
    """
    target = fields.Str()
    command = fields.Str()
    data = fields.Str()


class DeviceHealthSchema(Schema):
    """
    Device health and system info.
    """
    source = fields.Str()
    architecture = fields.Str()
    machine = fields.Str()
    processor = fields.Str()
    system = fields.Str()
    disk_usage = fields.Float()
    memory_usage = fields.Float()
    cpu_load = fields.Float()
    cpu_count = fields.Integer()
    cpu_temp = fields.Float()
    timestamp = fields.DateTime()


class ImageSchema(Schema):
    """
    Base64 encoded image.
    """
    source = fields.Str()
    b64image = fields.Str()
    content_type = fields.Str()
    timestamp = fields.DateTime()

    @staticmethod
    def encode_image(raw):
        """
        Encode raw image data (for example, JPEG) into base64.
        """
        return base64.b64encode(raw).decode('utf-8')

    @staticmethod
    def decode_image(str_b64):
        """
        Decode base64 string into raw image data (for example, JPEG).
        """
        return base64.b64decode(str_b64)
