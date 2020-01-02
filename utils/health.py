import psutil
import platform

from utils.config import config
from utils.messages import DeviceHealth


class Device:
    def __init__(self):
        self.architecture = platform.architecture()
        self.machine = platform.machine()
        self.processor = platform.processor()
        self.system = platform.system()

    def get_health(self):
        """
        Gets current device stats.
        """
        return DeviceHealth(
            architecture=self.architecture,
            machine=self.machine,
            processor=self.processor,
            system=self.system,
            memory_usage=psutil.virtual_memory().percent,
            cpu_load=psutil.getloadavg(),
            cpu_count=psutil.cpu_count(),
            disk_usage=psutil.disk_usage('/').percent,
            cpu_temp=0
        )


__the_device = None


def device():
    """
    Creates an Device instance
    """
    global __the_device
    if not __the_device:
        __the_device = Device()

    return __the_device
