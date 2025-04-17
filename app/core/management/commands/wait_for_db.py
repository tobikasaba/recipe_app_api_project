"""
Django command to wait for the database to be avaialable
"""

# used to make execution sleep
import time

# a possible error that might occur when trying to connect to the database before it is ready
from psycopg2 import OperationalError as Psycopg2OpError

# An error that might be thrown by the database depending on the stage of the process (if its not ready)
from django.db.utils import OperationalError

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Django command to wait for the database to be avaialable"""
    def handle(self, *args, **options):
        # stdout is the standout output used to log strings to the screen as our command is executing
        self.stdout.write('Waiting for database...')

        # tracks if DB is up yet
        db_up = False
        while db_up is False:
            try:
                # if the database isn't ready, it throws exception else sets db_up to true
                self.check(databases=['default'])
                db_up = True
            except(Psycopg2OpError, OperationalError):
                self.stdout.write('Database unavailable, waiting 1 second...')
                # sleep for one second, i.e. stop for one second and then try again
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS('Database available!'))
