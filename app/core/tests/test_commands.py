"""
Test custom Django management commands
"""

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

#mocking the check method in the Command
@patch('core.management.commands.wait_for_db.Command.check')
class CommandTests(SimpleTestCase):
    """Test custom Django management commands"""
    def test_wait_for_db_ready(self, patched_check):
        """Test waiting for database when database is available"""
        pass