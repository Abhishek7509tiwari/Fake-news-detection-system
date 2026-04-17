from flask import Flask, render_template, request, jsonify, session, redirect, url_for, Response
import sys
import os
import sqlite3
import csv
from datetime import datetime
from functools import wraps
from pathlib import Path

# Add project root to Python path
project_root = str(Path(__file__).parent.parent.parent.absolute())
if project_root not in sys.path:
    sys.path.append(project_root)

from src.core.pipeline import AutomatedPipeline

app = Flask(__name__)
# In production, use a secure secret key from environment variable
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "super_secret_admin_key_replace_me_in_prod")
pipeline = AutomatedPipeline()

# Database setup
DB_PATH = os.path.join(project_root, "src", "app_flask", "predictions.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                source_type TEXT,
                source_content TEXT,
                prediction TEXT,
                confidence REAL,
                reasoning TEXT
            )
        ''')
init_db()

def log_prediction(source_type, source_content, prediction, confidence, reasoning):
    try:
        with get_db() as conn:
            conn.execute('''
                INSERT INTO predictions (source_type, source_content, prediction, confidence, reasoning)
                VALUES (?, ?, ?, ?, ?)
            ''', (source_type, source_content, prediction, confidence, reasoning))
    except Exception as e:
        print(f"Failed to log prediction to DB: {e}")

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session:
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# --- Existing App Routes ---

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.form
    text = data.get('text')
    url = data.get('url')
    
    if not text and not url:
        return render_template('index.html', error="Please provide either a URL or text content.")
    
    if url:
        result = pipeline.run_url(url)
        content = url
        src_type = "URL"
    else:
        result = pipeline.run_text(text)
        content = text[:300]
        src_type = "TEXT"
        
    if "result" in result:
        log_prediction(src_type, content, result["result"], result.get("confidence", 0), result.get("reasoning", ""))
        
    return render_template('result.html', result=result)

@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    data = request.json
    text = data.get('text')
    url = data.get('url')
    
    if not text and not url:
        return jsonify({"error": "Please provide either a URL or text content."}), 400
    
    if url:
        result = pipeline.run_url(url)
        content = url
        src_type = "URL"
    else:
        result = pipeline.run_text(text)
        content = text[:300]
        src_type = "TEXT"
        
    if "result" in result:
        log_prediction(src_type, content, result["result"], result.get("confidence", 0), result.get("reasoning", ""))
        
    return jsonify(result)

# --- Admin Dashboard Routes ---

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form.get('email') or request.form.get('username')
        password = request.form.get('password')
        # Hardcoded credentials for Demo. In production, use a secure DB store.
        if email == 'admin@gmail.com' and password == 'password@123':
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('admin_login.html', error="Invalid credentials. Use admin@gmail.com / password@123")
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    # Filters
    from_date = request.args.get('from_date')
    to_date = request.args.get('to_date')
    category = request.args.get('category')

    query = "SELECT * FROM predictions WHERE 1=1"
    params = []

    if from_date:
        query += " AND date(timestamp) >= ?"
        params.append(from_date)
    if to_date:
        query += " AND date(timestamp) <= ?"
        params.append(to_date)
    if category and category != "ALL":
        query += " AND prediction = ?"
        params.append(category)

    query += " ORDER BY timestamp DESC"
    
    with get_db() as conn:
        records_cursor = conn.execute(query, params)
        records = [dict(ix) for ix in records_cursor.fetchall()]
        
        # Calculate stats
        total = len(records)
        fake_count = sum(1 for r in records if r['prediction'] == 'FAKE')
        real_count = sum(1 for r in records if r['prediction'] == 'REAL')
        avg_confidence = sum(r['confidence'] for r in records) / total if total > 0 else 0

    return render_template('admin_dashboard.html', 
                         records=records, 
                         total=total, 
                         fake_count=fake_count, 
                         real_count=real_count,
                         avg_confidence=avg_confidence)

@app.route('/admin/delete/<int:id>', methods=['POST'])
@login_required
def admin_delete(id):
    with get_db() as conn:
        conn.execute("DELETE FROM predictions WHERE id = ?", (id,))
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/export')
@login_required
def admin_export():
    with get_db() as conn:
        records = conn.execute("SELECT * FROM predictions ORDER BY timestamp DESC").fetchall()
        
    def generate():
        header = ["ID", "Timestamp", "Source Type", "Content", "Prediction", "Confidence", "Reasoning"]
        # Basic escaping for CSV conformity
        def safe_csv(val):
            val_str = str(val).replace('"', '""') # escape double quotes
            if ',' in val_str or '\n' in val_str or '"' in val_str:
                return f'"{val_str}"'
            return val_str
            
        yield ",".join(header) + "\n"
        for r in records:
            row = [
                safe_csv(r['id']),
                safe_csv(r['timestamp']),
                safe_csv(r['source_type']),
                safe_csv(r['source_content']),
                safe_csv(r['prediction']),
                safe_csv(round(r['confidence'], 4)),
                safe_csv(r['reasoning'])
            ]
            yield ",".join(row) + "\n"
            
    return Response(generate(), mimetype='text/csv', headers={"Content-Disposition": "attachment; filename=predictions_history.csv"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
