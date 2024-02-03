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

# SELECT ONE USER
@app.route('/user/update/<int:user_id>', methods=['GET'])
def user_update_view(user_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM User WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    return render_template('User/update.html', user=user)

# INSERT USER
@app.route('/user/insert', methods=['POST'])
def user_insert():
    if request.method == 'POST':
        name = request.form['name']
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO User (name) VALUES (?)', (name,))
        conn.commit()
        conn.close()
    return redirect(url_for('user'))

# DELETE USER
@app.route('/delete/<int:user_id>', methods=['POST'])
def user_delete(user_id):
    if request.method == 'POST':
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM User WHERE id = ?', (user_id,))
        conn.commit()
        conn.close()
    return redirect(url_for('user'))

# UPDATE USER
@app.route('/user/update_user/<int:user_id>', methods=['POST'])
def user_update(user_id):
    new_name = request.form.get('new_name')
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE User SET name = ? WHERE id = ?', (new_name, user_id))
        conn.commit()
    return redirect(url_for('user'))