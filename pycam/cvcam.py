import cv2
from config import cv_config


__cv_cap = None


def cv_cap():
    """
    Setup capture device
    """
    global __cv_cap

    if not __cv_cap:
        __cv_cap = cv2.VideoCapture(cv_config()['device'])

        # setup high res

    return __cv_cap


def cv_capture_jpeg_frame():
    """
    Capture low-res video frame
    """
    ret, frame = cv_cap().read()

    if ret:
        # scale to low res
        frame_height, frame_width = frame.shape[:2]
        target_width = cv_config()['video_width']
        scale = float(target_width) / frame_width
        target_height = int(scale * frame_height + 0.5)

        frame_lr = cv2.resize(frame, (target_width, target_height))

        # encode low res frame to JPEG
        quality = cv_config()['jpeg_quality']
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
        result, encimg = cv2.imencode('.jpg', frame_lr, encode_param)

        return encimg

    else:
        return None


def cv_capture_jpeg_still():
    """
    Capture high-res still
    """
    ret, frame = cv_cap().read()

    if ret:
        # encode to JPEG
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), cv_config()['quality']]
        result, encimg = cv2.imencode('.jpg', frame, encode_param)

        return encimg

    else:
        return None
