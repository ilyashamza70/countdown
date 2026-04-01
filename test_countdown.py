import unittest
from datetime import datetime, timedelta
from unittest import mock
from countdown import get_deadline, display_countdown

class TestCountdown(unittest.TestCase):
    
    def test_get_deadline_future(self):
        with mock.patch('builtins.input', return_value='31-12-2099 23:59'):
            deadline = get_deadline()
            self.assertTrue(deadline > datetime.now())

    def test_get_deadline_past(self):
        with mock.patch('builtins.input', side_effect=['01-01-2000 00:00', '31-12-2099 23:59']):
            deadline = get_deadline()
            self.assertTrue(deadline > datetime.now())
    
    def test_display_countdown(self):
        past_time = datetime.now() - timedelta(seconds=1)
        with mock.patch('time.sleep', return_value=None):
            with mock.patch('builtins.print') as mocked_print:
                display_countdown(past_time)
                mocked_print.assert_called_with('The deadline has passed!')

if __name__ == '__main__':
    unittest.main()
