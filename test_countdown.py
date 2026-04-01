import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from io import StringIO
import countdown


class TestGetDeadline(unittest.TestCase):
    """Test the get_deadline function"""
    
    @patch('countdown.input')
    def test_valid_future_deadline(self, mock_input):
        """Test with a valid future deadline"""
        future_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
        mock_input.return_value = future_date
        result = countdown.get_deadline()
        self.assertIsInstance(result, datetime)
        self.assertGreater(result, datetime.now())
    
    @patch('countdown.input')
    def test_invalid_format(self, mock_input):
        """Test with invalid date format, then valid one"""
        future_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
        mock_input.side_effect = ["invalid-date", future_date]
        result = countdown.get_deadline()
        self.assertIsInstance(result, datetime)
    
    @patch('countdown.input')
    def test_past_deadline_then_valid(self, mock_input):
        """Test with past deadline, then valid future one"""
        past_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
        future_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
        mock_input.side_effect = [past_date, future_date]
        result = countdown.get_deadline()
        self.assertGreater(result, datetime.now())


class TestDisplayCountdown(unittest.TestCase):
    """Test the display_countdown function"""
    
    @patch('countdown.time.sleep')
    @patch('countdown.print')
    def test_countdown_ends_when_deadline_passed(self, mock_print, mock_sleep):
        """Test that countdown ends when deadline is reached"""
        # Set deadline to 1 second in the past
        past_deadline = datetime.now() - timedelta(seconds=1)
        countdown.display_countdown(past_deadline)
        
        # Check that "The deadline has passed!" was printed
        calls = [str(call) for call in mock_print.call_args_list]
        self.assertTrue(any("The deadline has passed!" in str(call) for call in calls))
    
    @patch('countdown.time.sleep')
    @patch('countdown.print')
    def test_countdown_displays_remaining_time(self, mock_print, mock_sleep):
        """Test that countdown displays time correctly"""
        # Set up mock to stop after first iteration
        mock_sleep.side_effect = [None, KeyboardInterrupt()]
        
        future_deadline = datetime.now() + timedelta(seconds=10)
        
        try:
            countdown.display_countdown(future_deadline)
        except KeyboardInterrupt:
            pass
        
        # Verify print was called
        self.assertTrue(mock_print.called)


class TestMain(unittest.TestCase):
    """Test the main function"""
    
    @patch('countdown.display_countdown')
    @patch('countdown.get_deadline')
    @patch('countdown.print')
    def test_main_function(self, mock_print, mock_get_deadline, mock_display_countdown):
        """Test that main function orchestrates correctly"""
        mock_deadline = datetime.now() + timedelta(hours=1)
        mock_get_deadline.return_value = mock_deadline
        
        countdown.main()
        
        # Verify welcome message was printed
        self.assertTrue(mock_print.called)
        # Verify get_deadline was called
        self.assertTrue(mock_get_deadline.called)
        # Verify display_countdown was called with the deadline
        mock_display_countdown.assert_called_once_with(mock_deadline)


if __name__ == '__main__':
    unittest.main()
