from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

# SELECT ALL USER
@app.route('/user', methods=['GET'])
def user():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM User')
    users = cursor.fetchall()

    conn.close()

    return render_template('User/index.html', users=users)

# INSERT USER
@app.route('/user/insert', methods=['POST'])
def insert():
    if request.method == 'POST':
        name = request.form['name']

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        cursor.execute('INSERT INTO User (name) VALUES (?)', (name,))

        conn.commit()
        conn.close()

    return redirect(url_for('user'))

# DELETE USER
@app.route('/delete/<int:staff_id>', methods=['POST'])
def delete(staff_id):
    if request.method == 'POST':
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        cursor.execute('DELETE FROM User WHERE id = ?', (staff_id,))

        conn.commit()
        conn.close()

    return redirect(url_for('user'))