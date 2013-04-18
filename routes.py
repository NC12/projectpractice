import sqlite3
from flask import *
from functools import wraps

DATABASE = "merchandise.db"

app = Flask(__name__)
app.config.from_object(__name__)

app.secret_key = 'my precioussdfghjklcvbnm,'

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/welcome')
def welcome():
    return render_template('welcome.html')

@app.route('/log', methods=['GET', 'POST'])
def log():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = 'Invalid Credentials. Please try again.'
        else:
            session['logged_in'] = True
            return redirect(url_for('hello'))
    return render_template('log.html', error = error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('log'))

def login_required(test):
    @wraps(test)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return test(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('log'))
    return wrap

@app.route('/hello', methods=['GET', 'POST'])
@login_required
def hello():
    g.db = connect_db()
    cur = g.db.execute('SELECT name, file, price, quantity FROM merchandise')
    merchandise = [dict(name=row[0], file=row[1], price="{0:.2f}".format(row[2]), quantity=row[3]) for row in cur.fetchall()]
##    for item in merchandise:
##        number = request.form[item.name]
##        if number != 0:
##            total = number * item.price
##            quantity = item.quantity - number       
    g.db.close()
    return render_template('hello.html', merchandise = merchandise)
##
##def order():
##    error = None
##    if request.method == 'POST':
##        for item in merchandise:
##            number = request.form[item.name]
##            if number != 0:
##                total = number * item.price
##                quantity = item.quantity - number       
##    g.db.close()
    
if __name__ == '__main__':
    app.run(debug=True)
