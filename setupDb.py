import sqlite3

conn = sqlite3.connect('countdowns.db')
c = conn.cursor()

c.execute('''
          CREATE TABLE countdowns
          (id INTEGER PRIMARY KEY,
          deadline TEXT)
          ''')

conn.commit()
conn.close()
