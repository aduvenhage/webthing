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

        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _send_message(self, channel, **kwargs):
        """
        Send single message.
        Retry if rate limited.
        """
        print('post')
        response = self._slack_client.chat_postMessage(
            channel=channel,
            **kwargs
        )

        # check for errors
        if response["ok"] is False:
            # back off and retry if rate limited
            if response["headers"]["Retry-After"]:
                delay = int(response["headers"]["Retry-After"])
                logging.warning('Slack API rate limited. Waiting %d seconds.', delay)
                time.sleep(delay)

                return self._send_message(channel, **kwargs)

            else:
                logging.error('Slack request error. %s', response['error'])

    def _run(self):
        """
        Messenger thread intry point.
        """
        self._slack_client = slack.WebClient(token=self._api_token)

        while True:
            # grab next message from queue
            if not self._msg_queue.empty():
                message = self._msg_queue.get(timeout=1)

                try:
                    channel = message.pop('channel')
                    self._send_message(channel=channel, **message)

                except Exception as e:
                    logging.warning('Slack send message failed. %s', str(e))

            else:
                time.sleep(0.5)

    def add_message(self, message):
        """
        Add message to queue of messages to be sent out.
        """
        self._msg_queue.put(message)


__slack_messenger = None


def slack_messenger():
    """
    Creates a slack messenger instance
    """
    global __slack_messenger

    if not __slack_messenger:
        cfg = config()
        __slack_messenger = SlackMessenger(api_token='xoxb-989333962598-988995495575-IlmPHaKRPpyChFkjqbAyBHTd')

    return __slack_messenger
