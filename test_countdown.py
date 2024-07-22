import unittest
from datetime import datetime, timedelta
from countdown import get_deadline, display_countdown

class TestCountdown(unittest.TestCase):
    
    def test_get_deadline_future(self):
        with unittest.mock.patch('builtins.input', return_value='2099-12-31 23:59:59'):
            deadline = get_deadline()
            self.assertTrue(deadline > datetime.now())

    def test_get_deadline_past(self):
        with unittest.mock.patch('builtins.input', return_value='2000-01-01 00:00:00'):
            with self.assertRaises(SystemExit):
                get_deadline()
    
    def test_display_countdown(self):
        future_time = datetime.now() + timedelta(seconds=2)
        with unittest.mock.patch('time.sleep', return_value=None):
            with unittest.mock.patch('builtins.print') as mocked_print:
                display_countdown(future_time)
                mocked_print.assert_called_with('The deadline has passed!')

if __name__ == '__main__':
    unittest.main()
