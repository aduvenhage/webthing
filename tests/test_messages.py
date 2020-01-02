import unittest

from utils.messages import *


class TestMessageReflection(unittest.TestCase):

    @classmethod
    def setup_class(cls):
        pass

    def test_message_lookup(self):
        """
        Test message type lookup by string name.
        """
        msg_type = find_message_type('Command')
        self.assertTrue(msg_type.__name__ == 'Command')

    def test_message_encode(self):
        """
        Test message encoding
        """
        c1 = Command('n1', 'v1')
        e1 = encode_message(c1)

        expected_encoding = {
            'class': 'Command',
            'name': 'n1',
            'value': 'v1'
        }

        self.assertTrue(json.loads(e1) == expected_encoding)

    def test_message_decode(self):
        """
        Test message decoding
        """
        expected_encoding = {
            'class': 'Command',
            'name': 'n1',
            'value': 'v1'
        }

        e1 = json.dumps(expected_encoding)
        c1 = decode_message(e1, 'application/json')

        self.assertTrue(type(c1) == Command)
        self.assertTrue(c1.name == 'n1')
        self.assertTrue(c1.value == 'v1')
