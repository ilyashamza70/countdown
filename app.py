from flask import Flask, request, render_template, redirect, url_for, flash
from datetime import datetime
import sqlite3

app = Flask(__name__)
app.secret_key = 'supersecretkey'

def get_db_connection():
    conn = sqlite3.connect('countdowns.db')
    conn.row_factory = sqlite3.Row
    return conn

def save_countdown(deadline, ip_address):
    conn = get_db_connection()
    conn.execute('INSERT INTO countdowns (deadline, ip_address) VALUES (?, ?)', (deadline, ip_address))
    conn.commit()
    conn.close()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/countdown', methods=['POST'])
def countdown():
    deadline_str = request.form['deadline']
    ip_address = request.remote_addr
    try:
        deadline = datetime.strptime(deadline_str, "%d-%m-%YT%H:%M")
        if deadline < datetime.now():
            flash('The deadline must be in the future.')
            return redirect(url_for('home'))
        
        save_countdown(deadline_str, ip_address)
        
        return redirect(url_for('view_countdown', deadline=deadline_str))
    except ValueError:
        flash('Invalid format. Please enter the deadline in the format DD-MM-YYYYTHH:MM.')
        return redirect(url_for('home'))

@app.route('/countdown/<deadline>')
def view_countdown(deadline):
    try:
        deadline = datetime.strptime(deadline, "%d-%m-%YT%H:%M")
        now = datetime.now()
        remaining_time = deadline - now
        return render_template('countdown.html', remaining_time=remaining_time)
    except ValueError:
        flash('Invalid format. Please enter the deadline in the format DD-MM-YYYYTHH:MM.')
        return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)
