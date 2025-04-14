"""
Test custom Django management commands
"""
from email.policy import default
# patch used to mock the behaviour of the database
from unittest.mock import patch

# a possible error that might occur when trying to connect to the database before it is ready
from psycopg2 import OperationalError as Psycopg2Error

# a helper function in django that allows us to call a command by the name
# Call the command we are testing
from django.core.management import call_command

#An error that might be thrown by the database depending on the stage of the process
from django.db.utils import OperationalError

# base test class used for testing unit test
from django.test import SimpleTestCase

# Mocking the check method in the Command.
# This allows the testing to check if the database is ready
#  provided the path to the command that we are mocking 'check'.
#  Command.check is provided by the Base class.
#  This allows you to check the status of the database
@patch('core.management.commands.wait_for_db.Command.check')
class CommandTests(SimpleTestCase):
    """Test custom Django management commands"""
    def test_wait_for_db_ready(self, patched_check):
        """Test waiting for the database, when the database is ready"""
        # this ensures that when check is called inside the command in the testcase, return True
        patched_check.return_value = True

        # call the wait_for_db command to execute the code inside wait_for_db.
        # also checks that the command gets called
        call_command('wait_for_db')

        # ensures that the mocked value (the check object in the command {patched _check)
        # is called with the default parameters
        patched_check.assert_called_once_with(database=['default'])


    @patch('time.sleep') # Mock the 'time.sleep' function to prevent actual delays during the test
    def test_wait_for_db_delay(self, patched_sleep, patched_check):
        """Test waiting for the database, when getting Operational Error"""

        # Set the side_effect for patched_check to simulate the database readiness behaviour
        # Raise an exception if the database isn't ready using a side_effect
        # The side_effect allows us to simulate different exceptions and return values for each call
        # First 2 times: raise Psycopg2Error (simulating database not ready)
        # Next 3 times: raise OperationalError (still simulating database not ready)
        # 6th time: return True (simulating the database is ready)
        patched_check.side_effect = [Psycopg2Error] * 2 + \
            [OperationalError] * 3 + [True]

        call_command('wait_for_db')

        # Since we are raising 5 exceptions before returning True, the check method
        # should be called 6 times (2 Psycopg2Error + 3 OperationalError + 1 True).
        # This simulates waiting for the database to be ready.
        self.assertEqual(patched_check.call_count, 6)

        # checking that the patched_check is called with the database set to default
        patched_check.asser_called_with(database=['default'])