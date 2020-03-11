
import serial
from array import array
from zones import zones

from utils.config import config, get_logger
from utils.slackmsg import slack_messenger

cfg = config()
ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=0)
status_msg = array('B', [1, 4, 83])
event_msg = array('B', [1, 11, 83])
slack = slack_messenger()
logger = get_logger(__name__)


def check_msg(msg):
    return msg[-1] == sum(msg[:-1]) % 256


def get_msg(input, n):
    # wait for full message
    if len(input) >= n:
        # extract message
        msg = input[:n]
        del input[:n]

        # verify checksum
        if check_msg(msg) is True:
            return msg

    return None


def process_status_msg(input):
    msg = get_msg(input, 6)
    if msg:
        # ignore status message
        logger.debug('s - [%s]', msg)


def process_sensor_msg(input):
    msg = get_msg(input, 13)
    if msg:
        zone_id = msg[5]
        state = msg[9]
        battery_level = msg[10]

        zone = zones.get(zone_id)
        name = zone.get('name', '')
        is_alert = zone.get('alert', False)
        desc = '%s (%d)' % (name, zone_id)

        if state & 0x08 == 0x08:
            desc += ', bty_low=%d' % battery_level

        else:
            desc += ', bty=%d' % battery_level

        if state & 0x71 == 0x71:
            desc += ', event=open'
            is_open = True

        else:
            desc += ', event=closed'
            is_open = False

        logger.debug('e - %s - [%s]', desc, msg)

        if is_open and is_alert:
            slack.add_message({
                'channel': '#alerts',
                'text': desc
            })

        elif cfg.debug:
            slack.add_message({
                'channel': '#random',
                'text': desc
            })


def main():
    input = array('B')
    while True:
        # read data from port
        s = ser.read(64)
        if len(s) > 0:
            input.extend(s)

        # scan through data and process messages
        if len(input) > 3:
            header = input[:3]

            # process status message
            if header == status_msg:
                process_status_msg(input)

            # process sensor event message
            elif header == event_msg:
                process_sensor_msg(input)

            # just scan through data if nothing matches
            else:
                logger.debug('u - %s', input)
                if cfg.debug:
                    slack.add_message({
                        'channel': '#random',
                        'text': 'u - ' + str(input)
                    })

                input.pop(0)


if __name__ == '__main__':
    main()
