# coding: utf-8
# author: maxint <NOT_SPAM_lnychina@gmail.com>

import unittest
import rect


class RectTest(unittest.TestCase):
    def test_parse(self):
        self.assertEqual(rect.parse_rect('0,0,0,0'), rect.Rect())
        self.assertEqual(rect.parse_rect('1,2,3,4'), rect.Rect(1, 2, 3, 4))
        self.assertEqual(rect.parse_rect('-1,2,3,4'), rect.Rect(-1, 2, 3, 4))
        self.assertRaises(AssertionError, lambda : rect.parse_rect('0,1,0,1'))
        self.assertEqual(rect.parse_rect_with_index('304	(0,0,0)	(1,2,3,4)'), (304, rect.Rect(1, 2, 3, 4)))
        self.assertRaises(AssertionError, lambda : rect.parse_rect_with_index('304	(0,0,0)	(474,573,482,573)'))


if __name__ == '__main__':
    unittest.main()