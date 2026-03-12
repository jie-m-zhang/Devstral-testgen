"""
Test to reproduce the issue where Signal.send_robust() doesn't log exceptions
raised in receivers.

This test should:
- FAIL on base commit (965d2d95c630939b53eb60d9c169f5dfc77ee0c6) - no logging occurs
- PASS on head commit (65dfb06a1ab56c238cc80f5e1c31f61210c4577d) - logging is present
"""

import logging
from django.dispatch import Signal
from django.test import SimpleTestCase

# Create a signal for testing
test_signal = Signal()

def failing_receiver(**kwargs):
    """A receiver that raises an exception"""
    raise ValueError("Test exception in receiver")

class SignalLoggingTest(SimpleTestCase):
    def test_send_robust_logs_exceptions(self):
        """Test that exceptions in signal receivers are logged"""
        # Set up a log handler to capture log messages
        log_handler = logging.Handler()
        captured_logs = []

        class ListHandler(logging.Handler):
            def emit(self, record):
                captured_logs.append(record)

        # Get the django.dispatch logger and add our handler
        logger = logging.getLogger('django.dispatch')
        logger.setLevel(logging.ERROR)
        log_handler = ListHandler()
        logger.addHandler(log_handler)

        try:
            # Connect the failing receiver
            test_signal.connect(failing_receiver)

            # Clear any previous logs
            captured_logs.clear()

            # Send the signal - this should cause an exception in the receiver
            result = test_signal.send_robust(sender=self)

            # Verify that the receiver failed
            self.assertEqual(len(result), 1)
            receiver, response = result[0]
            self.assertIsInstance(response, ValueError)
            self.assertEqual(str(response), "Test exception in receiver")

            # Verify that the exception was logged
            # This is the key assertion - it should FAIL on base commit (no logs)
            # and PASS on head commit (logs present)
            self.assertTrue(len(captured_logs) > 0,
                          "No log messages were captured. Expected logging of exception in Signal.send_robust()")

            if captured_logs:
                log_record = captured_logs[0]
                self.assertEqual(log_record.levelno, logging.ERROR)
                self.assertIn("Error calling", log_record.getMessage())
                self.assertIn("failing_receiver", log_record.getMessage())
                self.assertIn("Test exception in receiver", log_record.getMessage())
                self.assertTrue(log_record.exc_info is not None,
                              "Expected exc_info to be set in log record")

        finally:
            # Clean up
            test_signal.disconnect(failing_receiver)
            logger.removeHandler(log_handler)

if __name__ == '__main__':
    import django
    from django.conf import settings

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
            ],
            SECRET_KEY='test-secret-key',
        )
        django.setup()

    # Run the test
    test_case = SignalLoggingTest()
    test_case.test_send_robust_logs_exceptions()
    print("Test passed - issue is fixed")