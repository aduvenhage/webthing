from picamera import PiCamera
from io import BytesIO
import base64
import time

from utils.config import config
from utils.messages import Image


class PiCapture:

    def __init__(self, video_width=320, jpeg_quality=90):
        """
        see: https://picamera.readthedocs.io/en/latest/fov.html
        see: https://picamera.readthedocs.io/en/latest/recipes1.html
        """
        self._camera = PiCamera()
        self._camera.resolution = (3280, 2464)
        self._camera.start_preview()

        self._aspect = 3280 / 2464
        self.__video_width = video_width
        self.__video_height = int(video_width / self._aspect)
        self.__jpeg_quality = jpeg_quality

    def capture_jpeg_frame(self):
        """
        Capture low-res video frame
        """
        try:
            stream = BytesIO()
            self._camera.capture(stream,
                                 format='jpeg', use_video_port=True,
                                 resize=(self.__video_width, self.__video_height),
                                 quality=self.__jpeg_quality)

            stream.seek(0)
            return Image(b64image=base64.b64encode(stream.getvalue()).decode('utf-8'),
                         content_type='image/jpeg',
                         timestamp_ns=time.time_ns())

        except Exception:
            raise

    def capture_jpeg_still(self):
        """
        Capture high-res still
        """
        try:
            stream = BytesIO()
            self._camera.capture(stream,
                                 format='jpeg', use_video_port=False,
                                 resize=None, quality=self.__jpeg_quality)

            stream.seek(0)
            return Image(b64image=base64.b64encode(stream.getvalue()).decode('utf-8'),
                         content_type='image/jpeg',
                         timestamp_ns=time.time_ns())

        except Exception:
            return None


_pi_capture = None


def picap():
    """
    Creates PiCam capture instance
    """
    global _pi_capture

    if not _pi_capture:
        cfg = config()
        cfg.get('JPEG_QUALITY', 90)
        cfg.get('VIDEO_WIDTH', 320)

        _pi_capture = PiCapture(jpeg_quality=cfg.JPEG_QUALITY,
                                 video_width=cfg.VIDEO_WIDTH)

    return _pi_capture
