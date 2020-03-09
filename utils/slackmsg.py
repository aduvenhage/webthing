import threading
import queue
import slack
import time
import logging

from utils.config import config


class SlackMessenger:
    """
    Slack client message processing thread.
    """

    def __init__(self, api_token):
        """
        Create slack messenger thread.
        """
        self._msg_queue = queue.Queue()
        self._api_token = api_token
        self._slack_client = slack.WebClient(token=api_token)

        self._message = None
        self._channel = ''
        self._error_count = 0
        self._msg_backoff_s = 0

        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _send_message(self):
        """
        Try to send current message.
        """
        try:
            response = self._slack_client.chat_postMessage(
                channel=self._channel,
                **self._message
            )

        except slack.errors.SlackApiError as e:
            response = e.response

        # check for errors
        if response["ok"] is False:
            # back off and retry if rate limited
            if response["error"]:
                self._msg_backoff_s = 4
                logging.warning('Slack request error. %s', response['error'])

            elif response["headers"]["Retry-After"]:
                self._msg_backoff_s = int(response["headers"]["Retry-After"])
                logging.warning('Slack API rate limited.')

            else:
                self._msg_backoff_s = 4
                logging.warning('Slack request error. %s', 'Unknown error.')

            self._error_count += 1
            if self._error_count > 3:
                logging.error('Too many errors. Message dropped.')
                self._message = None

        else:
            logging.debug('Message sent on %s. %s', self._channel, self._message)
            self._message = None

    def _run(self):
        """
        Messenger thread intry point.
        """
        self._slack_client = slack.WebClient(token=self._api_token)

        while True:
            # grab next message from user queue if not busy
            if self._message is None and not self._msg_queue.empty():
                self._message = self._msg_queue.get(timeout=1)
                self._channel = self._message.pop('channel')
                self._error_count = 0
                self._msg_backoff_s = 0
                logging.debug('New message on %s. %s', self._channel, self._message)

            # try to send message
            if self._message is not None:
                if self._msg_backoff_s > 0:
                    logging.info('Waiting for %d seconds.', self._msg_backoff_s)
                    time.sleep(self._msg_backoff_s)

                self._send_message()

            else:
                time.sleep(0.5)

    def add_message(self, message):
        """
        Add message to queue of messages to be sent out.
        """
        self._msg_queue.put(message)

    def queue_size(self):
        """
        Returns number of messages waiting to be sent
        """
        return len(self._msg_queue)


__slack_messenger = None


def slack_messenger():
    """
    Creates a slack messenger instance
    """
    global __slack_messenger

    if not __slack_messenger:
        cfg = config()
        cfg.SLACK_TOKEN = cfg.get('SLACK_TOKEN', '')

        __slack_messenger = SlackMessenger(api_token=cfg.SLACK_TOKEN)

    return __slack_messenger
