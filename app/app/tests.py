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

