from abc import ABC, abstractmethod


class Camera(ABC):
    """
    Base class for all camera interfaces.
    """
    def __init__(self):
        super().__init__()

    @abstractmethod
    def capture_jpeg_frame(self):
        pass

    @abstractmethod
    def capture_jpeg_still(self):
        pass
