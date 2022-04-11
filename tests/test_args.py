import unittest

from scrycall.scry_args import parse_args, ArgumentError


class TestQueries(unittest.TestCase):
    def test_noquery(self):
        with self.assertRaises(ArgumentError):
            args = parse_args([])

    def test_name_only(self):
        args = parse_args(["venser", "t:creature"])
        self.assertEqual(args.query, "venser t:creature")


class TestFormats(unittest.TestCase):
    def test_attribute_name(self):
        args = parse_args(["shock", "--format", "%n %r"])
        self.assertEqual(args.formatting, "%n %r")


class TestNulls(unittest.TestCase):
    def test_default_null(self):
        args = parse_args(["shock"])
        self.assertEqual(args.null, "")

    def test_custom_null(self):
        args = parse_args(["shock", "--null", "na"])
        self.assertEqual(args.null, "na")
