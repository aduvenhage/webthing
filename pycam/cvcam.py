import cv2
from config import cv_config


class CvCapture:
    def __init__(self, device=0, video_width=320, jpeg_quality=90):
        """
        Create capture device
        """
        self.__cv_cap = cv2.VideoCapture(device)
        self.__video_width = video_width
        self.__video_height = 0
        self.__jpeg_quality = jpeg_quality

        self.__encode_param = [
            int(cv2.IMWRITE_JPEG_QUALITY),
            self.__jpeg_quality
        ]

    def capture_jpeg_frame(self):
        """
        Capture low-res video frame
        """
        ret, frame = self.__cv_cap.read()

        if ret:
            # calc video scale
            if not self.__video_height:
                frame_height, frame_width = frame.shape[:2]
                scale = float(self.__video_width) / frame_width
                self.__video_height = int(scale * frame_height + 0.5)

            # scale to low res
            if self.__video_height:
                frame_lr = cv2.resize(frame, (self.__video_width, self.__video_height))

                # encode low res frame to JPEG
                result, encimg = cv2.imencode('.jpg', frame_lr, self.__encode_param)
                return encimg

        return None

    def capture_jpeg_still(self, quality=90):
        """
        Capture high-res still
        """
        ret, frame = self.__cv_cap.read()

        if ret:
            # encode to JPEG
            result, encimg = cv2.imencode('.jpg', frame, self.__encode_param)
            return encimg

        return None


__cv_capture = None


def cv():
    """
    Creates OpenCV capture instance
    """
    global __cv_capture

    if not __cv_capture:
        __cv_capture = CvCapture(device=cv_config()['device'],
                                 jpeg_quality=cv_config()['jpeg_quality'],
                                 video_width=cv_config()['video_width'])

    return __cv_capture
