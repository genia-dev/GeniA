import unittest

from genia.utils.utils import is_blank


class UtilsTests(unittest.TestCase):
    def test_empty_string(self):
        self.assertTrue(is_blank(""))

    def test_blanks_string(self):
        self.assertTrue(is_blank(" "))

    def test_newline(self):
        self.assertTrue(is_blank("\n"))

    def test_none(self):
        self.assertTrue(is_blank(None))

    def test_genia_is_cool(self):
        self.assertFalse(is_blank("genia_is_cool"))


if __name__ == "__main__":
    unittest.main()
