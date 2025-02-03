"""sample tests"""


from django.test import SimpleTestCase

from . import calc


class CalcTest(SimpleTestCase):
    """
    Test the calc module.
    """
    def test_add_numbers(self):
        """
        Test adding two numbers.
        :return:
        """
        res = calc.add(5, 6)
        self.assertEqual(res, 11)


    def test_subtract_numbers(self):
        """
        Test subtracting two numbers.
        :return:
        """
        res = calc.subtract(10, 15)
        self.assertEqual(res, 5)
