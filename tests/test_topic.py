import unittest

from utils.topic import get_topic_match


class TestTopic(unittest.TestCase):

    @classmethod
    def setup_class(cls):
        pass

    def test_topic_matches(self):
        self.assertTrue(get_topic_match('aa.bb.*', 'aa.bb.cc'))
        self.assertTrue(get_topic_match('aa.*.cc', 'aa.bb.cc'))
        self.assertTrue(get_topic_match('*.bb.cc', 'aa.bb.cc'))

        self.assertTrue(get_topic_match('aa.bb.cc.*', 'aa.bb.cc.dd'))
        self.assertTrue(get_topic_match('aa.bb.*.dd', 'aa.bb.cc.dd'))
        self.assertTrue(get_topic_match('aa.*.cc.dd', 'aa.bb.cc.dd'))
        self.assertTrue(get_topic_match('*.bb.cc.dd', 'aa.bb.cc.dd'))

        self.assertTrue(get_topic_match('aa.*.*', 'aa.bb.cc'))
        self.assertTrue(get_topic_match('*.*.*', 'aa.bb.cc'))

        self.assertTrue(get_topic_match('#.cc', 'aa.bb.cc'))
        self.assertTrue(get_topic_match('#', 'aa.bb.cc'))
        self.assertTrue(get_topic_match('aa.#', 'aa.bb.cc'))

        self.assertTrue(get_topic_match('#.dd', 'aa.bb.cc.dd'))
        self.assertTrue(get_topic_match('aa.#.dd', 'aa.bb.cc.dd'))

    def test_topic_fails(self):
        self.assertFalse(get_topic_match('aa.bb.*', 'aa.bb'))
        self.assertFalse(get_topic_match('*.*', 'aa'))
        self.assertFalse(get_topic_match('aa.bb.*.dd', 'aa.bb.dd'))
