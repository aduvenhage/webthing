
class Topic:
    """
    System topics are built as 'category.sub_category.user_id.device_id.label':

    - category: message/channel type
    - sub_category: message/channel sub-type
    - user_id: user name
    - device_id: device identifier or name
    - label: user defined label for devices

    """

    @classmethod
    def build_topic(cls, category, sub_category, user_id, device_id, label, delimiter='.'):
        args = [category,
                sub_category,
                user_id,
                label,
                device_id]

        return delimiter.join(args)

    @classmethod
    def get_topic_category(cls, topic, delimiter='.'):
        return topic.split(delimiter)[0]

    @classmethod
    def get_topic_sub_category(cls, topic, delimiter='.'):
        return topic.split(delimiter)[1]

    @classmethod
    def get_topic_user_id(cls, topic, delimiter='.'):
        return topic.split(delimiter)[2]

    @classmethod
    def get_topic_label(cls, topic, delimiter='.'):
        return topic.split(delimiter)[3]

    @classmethod
    def get_topic_device_id(cls, topic, delimiter='.'):
        return topic.split(delimiter)[4]
