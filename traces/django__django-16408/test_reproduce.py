"""
Test to reproduce the issue with multi-level FilteredRelation and select_related()
"""

import os
import sys
import django
from django.conf import settings

# Add the tests directory to the path so we can import known_related_objects
sys.path.insert(0, '/testbed/tests')

# Configure Django settings
if not settings.configured:
    settings.configure(
        DEBUG=True,
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            }
        },
        INSTALLED_APPS=[
            'django.contrib.contenttypes',
            'django.contrib.auth',
            'known_related_objects',
        ],
        SECRET_KEY='test-secret-key',
    )

# Setup Django
django.setup()

from django.db.models import FilteredRelation
from django.test import TestCase
from known_related_objects.models import Organiser, Pool, PoolStyle, Tournament

class TestMultiLevelFilteredRelation(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create test data
        cls.t1 = Tournament.objects.create(name="Tournament 1")
        cls.t2 = Tournament.objects.create(name="Tournament 2")
        cls.o1 = Organiser.objects.create(name="Organiser 1")

        # Create pools
        cls.p1 = Pool.objects.create(
            name="T1 Pool 1", tournament=cls.t1, organiser=cls.o1
        )
        cls.p2 = Pool.objects.create(
            name="T1 Pool 2", tournament=cls.t1, organiser=cls.o1
        )
        cls.p3 = Pool.objects.create(
            name="T2 Pool 1", tournament=cls.t2, organiser=cls.o1
        )

        # Create pool styles
        cls.ps1 = PoolStyle.objects.create(name="T1 Pool 2 Style", pool=cls.p2)
        cls.ps2 = PoolStyle.objects.create(name="T2 Pool 1 Style", pool=cls.p3)
        cls.ps3 = PoolStyle.objects.create(
            name="T1 Pool 1/3 Style", pool=cls.p1, another_pool=cls.p3
        )

    def test_wrong_select_related(self):
        """
        Test that multi-level FilteredRelation with select_related() sets the correct related object.
        This test should FAIL on the buggy version and PASS on the fixed version.
        """
        p = list(PoolStyle.objects.annotate(
            tournament_pool=FilteredRelation('pool__tournament__pool'),
        ).select_related('tournament_pool'))

        # The assertion that fails on buggy code
        # p[0].pool.tournament should equal p[0].tournament_pool.tournament
        self.assertEqual(p[0].pool.tournament, p[0].tournament_pool.tournament,
                      f"Expected {p[0].pool.tournament}, got {p[0].tournament_pool.tournament}")

if __name__ == '__main__':
    import unittest
    from django.test.utils import get_runner
    from django.test.runner import DiscoverRunner

    runner_class = DiscoverRunner
    test_runner = runner_class(verbosity=2, interactive=False, keepdb=False)
    failures = test_runner.run_tests(['__main__'])

    if failures:
        sys.exit(1)
    else:
        sys.exit(0)