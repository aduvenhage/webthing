from utils.message_base import *


@message
class Command(Message):
    """
    Simple key/value type commands.
    """
    def __init__(self, name=None, value=None):
        self.name = name
        self.value = value


@message
class DeviceHealth(Message):
    """
    Device health and system info.
    """
    def __init__(self, source=None, architecture=None, machine=None, processor=None, 
                 system=None, memory_usage=None, cpu_load=None, cpu_count=None,
                 disk_usage=None, cpu_temp=None, timestamp_ns=None):
        self.source = source
        self.architecture = architecture
        self.machine = machine
        self.processor = processor
        self.system = system
        self.memory_usage = memory_usage
        self.cpu_load = cpu_load
        self.cpu_count = cpu_count
        self.disk_usage = disk_usage
        self.cpu_temp = cpu_temp
        self.timestamp_ns = timestamp_ns


@message
class Image(Message):
    """
    Base64 encoded image.
    """
    def __init__(self, source=None, b64image=None, content_type=None, timestamp_ns=None):
        self.source = source
        self.b64image = b64image
        self.content_type = content_type
        self.timestamp_ns = timestamp_ns
