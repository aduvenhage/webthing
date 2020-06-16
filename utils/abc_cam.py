from abc import ABC, abstractmethod


class Camera(ABC):
    """
    Base class for all camera interfaces.
    Capture methods should be thread safe.
    """
    def __init__(self):
        super().__init__()

    @abstractmethod
    def capture_jpeg_frame(self):
        pass

    @abstractmethod
    def capture_jpeg_still(self):
        pass
