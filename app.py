from flask import Flask, request, render_template, redirect, url_for, flash
from datetime import datetime, timezone
import logging
import secrets
import sqlite3

app = Flask(__name__)
app.secret_key = 'supersecretkey'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)

def ensure_schema(conn):
    conn.execute(
        'CREATE TABLE IF NOT EXISTS countdowns '
        '(id INTEGER PRIMARY KEY, deadline TEXT, ip_address TEXT)'
    )
    columns = {row['name'] for row in conn.execute('PRAGMA table_info(countdowns)')}
    # Keep migrations tiny and safe for existing installs.
    if 'share_token' not in columns:
        conn.execute('ALTER TABLE countdowns ADD COLUMN share_token TEXT')
    if 'timezone' not in columns:
        conn.execute('ALTER TABLE countdowns ADD COLUMN timezone TEXT')
    if 'timezone_offset' not in columns:
        conn.execute('ALTER TABLE countdowns ADD COLUMN timezone_offset INTEGER')
    if 'created_at' not in columns:
        conn.execute('ALTER TABLE countdowns ADD COLUMN created_at TEXT')


def get_db_connection():
    conn = sqlite3.connect('countdowns.db')
    conn.row_factory = sqlite3.Row
    ensure_schema(conn)
    return conn

def save_countdown(deadline_utc, ip_address, timezone_name, timezone_offset):
    conn = get_db_connection()
    share_token = secrets.token_urlsafe(8)
    created_at = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    conn.execute(
        'INSERT INTO countdowns (deadline, ip_address, share_token, timezone, timezone_offset, created_at) '
        'VALUES (?, ?, ?, ?, ?, ?)',
        (deadline_utc, ip_address, share_token, timezone_name, timezone_offset, created_at)
    )
    conn.commit()
    conn.close()
    logging.info('Saved countdown for ip=%s deadline=%s token=%s', ip_address, deadline_utc, share_token)
    return share_token


def get_latest_countdown_for_ip(ip_address):
    conn = get_db_connection()
    row = conn.execute(
        'SELECT * FROM countdowns WHERE ip_address = ? ORDER BY id DESC LIMIT 1',
        (ip_address,)
    ).fetchone()
    conn.close()
    return row


def get_countdown_by_token(token):
    conn = get_db_connection()
    row = conn.execute('SELECT * FROM countdowns WHERE share_token = ?', (token,)).fetchone()
    conn.close()
    return row


def parse_deadline(deadline_utc_str, deadline_local_str):
    if deadline_utc_str:
        return datetime.fromisoformat(deadline_utc_str.replace('Z', '+00:00'))
    if deadline_local_str:
        # Fallback when JS is disabled; assumes server-local timezone.
        return datetime.strptime(deadline_local_str, "%Y-%m-%dT%H:%M").astimezone()
    raise ValueError('Missing deadline')

@app.route('/')
def home():
    ip_address = request.remote_addr or 'unknown'
    latest = get_latest_countdown_for_ip(ip_address)
    if latest and latest['share_token']:
        try:
            deadline_utc = datetime.fromisoformat(latest['deadline'].replace('Z', '+00:00'))
            if deadline_utc > datetime.now(timezone.utc):
                return redirect(url_for('view_countdown', token=latest['share_token']))
        except ValueError:
            logging.exception('Invalid stored deadline for ip=%s', ip_address)
    return render_template('index.html')

@app.route('/countdown', methods=['POST'])
def countdown():
    deadline_utc_str = request.form.get('deadline_utc', '').strip()
    deadline_local_str = request.form.get('deadline', '').strip()
    timezone_name = request.form.get('timezone', '').strip() or 'Local'
    timezone_offset_str = request.form.get('timezone_offset', '').strip()
    timezone_offset = int(timezone_offset_str) if timezone_offset_str else None
    ip_address = request.remote_addr or 'unknown'
    if not deadline_utc_str and not deadline_local_str:
        flash('Please provide a deadline.')
        logging.warning('Missing deadline from ip=%s', ip_address)
        return redirect(url_for('home'))
    try:
        deadline = parse_deadline(deadline_utc_str, deadline_local_str)
        deadline_utc = deadline.astimezone(timezone.utc)
        if deadline_utc < datetime.now(timezone.utc):
            flash('The deadline must be in the future.')
            logging.info('Rejected past deadline=%s ip=%s', deadline_utc, ip_address)
            return redirect(url_for('home'))

        deadline_utc_iso = deadline_utc.isoformat().replace('+00:00', 'Z')
        token = save_countdown(deadline_utc_iso, ip_address, timezone_name, timezone_offset)

        return redirect(url_for('view_countdown', token=token))
    except ValueError:
        flash('Invalid format. Please enter the deadline in the format YYYY-MM-DDTHH:MM.')
        logging.exception('Invalid deadline format ip=%s value=%s', ip_address, deadline_local_str)
        return redirect(url_for('home'))

@app.route('/countdown/<token>')
def view_countdown(token):
    row = get_countdown_by_token(token)
    if not row:
        flash('Countdown not found.')
        logging.warning('Countdown token not found token=%s', token)
        return redirect(url_for('home'))
    try:
        deadline_utc = datetime.fromisoformat(row['deadline'].replace('Z', '+00:00'))
        remaining_time = deadline_utc - datetime.now(timezone.utc)
        share_url = url_for('view_countdown', token=token, _external=True)
        timezone_name = row['timezone'] or 'Local'
        return render_template(
            'countdown.html',
            remaining_time=remaining_time,
            deadline_utc=row['deadline'],
            share_url=share_url,
            timezone_name=timezone_name
        )
    except ValueError:
        flash('Invalid countdown data.')
        logging.exception('Invalid countdown data token=%s', token)
        return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)
