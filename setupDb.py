import sqlite3

conn = sqlite3.connect('countdowns.db')
c = conn.cursor()

c.execute('''
          CREATE TABLE countdowns
          (id INTEGER PRIMARY KEY,
          deadline TEXT,
          ip_address TEXT,
          share_token TEXT,
          timezone TEXT,
          timezone_offset INTEGER,
          created_at TEXT)
          ''')

conn.commit()
conn.close()
