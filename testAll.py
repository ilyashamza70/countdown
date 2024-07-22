import unittest
from app import app, get_db_connection
from flask import request
from datetime import datetime, timedelta
import sqlite3

class TestCountdownApp(unittest.TestCase):

    def setUp(self):
        # Set up the test client
        self.app = app.test_client()
        self.app.testing = True
        
        # Set up the test database
        self.conn = get_db_connection()
        self.conn.execute('DELETE FROM countdowns')
        self.conn.commit()

    def tearDown(self):
        # Tear down the test database
        self.conn.close()

    def test_home_page(self):
        # Test the home page loads correctly
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Countdown Timer Viewer', response.data)

    def test_countdown_page(self):
        # Test the countdown page loads correctly
        deadline = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M")
        response = self.app.post('/countdown', data=dict(deadline=deadline), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Time remaining:', response.data)

    def test_invalid_deadline(self):
        # Test an invalid deadline
        deadline = 'invalid-date'
        response = self.app.post('/countdown', data=dict(deadline=deadline), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid format. Please enter the deadline in the format YYYY-MM-DDTHH:MM.', response.data)

    def test_past_deadline(self):
        # Test a past deadline
        deadline = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M")
        response = self.app.post('/countdown', data=dict(deadline=deadline), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'The deadline must be in the future.', response.data)

    def test_db_entry(self):
        # Test the database entry
        deadline = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M")
        ip_address = '127.0.0.1'
        self.conn.execute('INSERT INTO countdowns (deadline, ip_address) VALUES (?, ?)', (deadline, ip_address))
        self.conn.commit()
        countdowns = self.conn.execute('SELECT * FROM countdowns').fetchall()
        self.assertEqual(len(countdowns), 1)
        self.assertEqual(countdowns[0]['deadline'], deadline)
        self.assertEqual(countdowns[0]['ip_address'], ip_address)

if __name__ == '__main__':
    unittest.main()
