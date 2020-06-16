import psutil
import platform
import datetime

from utils.messages import DeviceHealthSchema


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
        du = psutil.disk_usage('/')
        health = dict(
            architecture=self.architecture[0],
            machine=self.machine,
            processor=self.processor,
            system=self.system,
            memory_usage=psutil.virtual_memory().percent,
            cpu_load=psutil.getloadavg()[0],
            cpu_count=psutil.cpu_count(),
            disk_usage=(1.0 - du.free / du.total) * 100,
            cpu_temp=0,
            timestamp=datetime.datetime.now(),
            connected=False,
            status='',
            temperature=0,
            voltage=0
        )

        schema = DeviceHealthSchema()
        return schema.dump(health)


__the_device = None


def device():
    """
    Creates an Device instance
    """
    global __the_device
    if not __the_device:
        __the_device = Device()

    return __the_device
