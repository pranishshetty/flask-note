from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

db_path = 'notes.db'

# Initialize database (optional if you already used init_db.py)
def init_db():
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL)''')
        c.execute('''CREATE TABLE IF NOT EXISTS notes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        content TEXT NOT NULL,
                        FOREIGN KEY(user_id) REFERENCES users(id))''')

init_db()

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        c.execute("SELECT content FROM notes WHERE user_id = ?", (session['user_id'],))
        notes = [row[0] for row in c.fetchall()]
    return render_template('index.html', notes=notes)

@app.route('/add', methods=['POST'])
def add_note():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    note = request.form.get('note')
    if note:
        with sqlite3.connect(db_path) as conn:
            c = conn.cursor()
            c.execute("INSERT INTO notes (user_id, content) VALUES (?, ?)", (session['user_id'], note))
            conn.commit()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        print("Register form submitted")  # Debug line
        username = request.form['username']
        password = request.form['password']
        print(f"Username: {username}, Password: {password}")  # Debug line

        with sqlite3.connect(db_path) as conn:
            c = conn.cursor()
            try:
                c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
                conn.commit()
                print("User registered successfully")  # Debug line
                return redirect(url_for('login'))
            except sqlite3.IntegrityError:
                print("Username already exists!")  # Debug line
                return render_template('register.html', error="Username already exists")
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        with sqlite3.connect(db_path) as conn:
            c = conn.cursor()
            c.execute("SELECT id FROM users WHERE username = ? AND password = ?", (username, password))
            user = c.fetchone()
            if user:
                session['user_id'] = user[0]
                return redirect(url_for('index'))
            else:
                return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
