import json


class Message:
    message_type_dict = {}

    @classmethod
    def message_type(cls):
        """
        Returns the message class name
        """
        return cls.__name__

    def encode(self):
        """
        Joins the message class/type with the message atributes,
        encode to JSON and return.

        NOTE: class/type is used to construct correct message sub-type
        on decode.
        """
        return json.dumps({
            'class': self.message_type(),
            **self.__dict__
        })


def message(cls):
    """
    Decorator that declares cls as a message type (add to type lookup, etc).
    """
    Message.message_type_dict[cls.message_type()] = cls
    return cls


def encode_message(msg_obj):
    """
    Encode message object into JSON.
    Returns: JSON string
    """
    return msg_obj.encode()


def encoded_content_type():
    return 'application/json'


def find_message_type(type_name):
    """
    Lookup message type from message type name string.
    Returns: Message sub-type
    """
    try:
        return Message.message_type_dict[type_name]

    except Exception:
        raise Exception("Unknown Message sub-type '%s'" % (type_name))


def decode_message(msg_str):
    """
    Decode JSON string into message object of correct type/class.
    Returns: message object
    """
    msg_obj = json.loads(msg_str)
    if msg_obj is not None:
        msg_type_name = msg_obj.pop('class')
        msg_type = find_message_type(msg_type_name)

        # construct new message (of msg_type) with msg_obj dict as parameters
        return msg_type(**msg_obj)

    raise Exception('Message decoding failed on: %s' % (msg_str))
