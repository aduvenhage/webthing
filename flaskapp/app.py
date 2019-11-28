from utils import config
from . import create_app


app = create_app()
config = config.get_config()


value = config.CAMERA_ID