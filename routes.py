import sqlite3
from datetime import datetime
from flask import *
from flask_mail import *
from functools import wraps
from flask.ext.wtf import *
from wtforms import *
from werkzeug import generate_password_hash, check_password_hash

MERCHANDISE = "merchandise.db"
DATABASE = "data.db"

app = Flask(__name__)
app.config.from_object(__name__)
app.secret_key = 'secret key is secret,'

MAIL_SERVER = 'smtp.example.com'
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_USERNAME = 'username'
MAIL_PASSWORD = 'password'
mail = Mail(app)


def connect_db():
    return sqlite3.connect(app.config['MERCHANDISE'])

def connect_data():
    return sqlite3.connect(app.config['DATABASE'])

def send_email(subject, sender, recipients, text_body):
    msg = Message(subject, sender = sender, recipients = recipients)
    msg.body = text_body
    mail.send(msg)
    
class signup_form(Form):
    username = TextField('Username:', [validators.Required()])
    password = PasswordField('Password:', [validators.Required(), validators.EqualTo('confirm', message='Oops! Passwords do not match. Please try again')])
    confirm = PasswordField('Confirm Password:', [validators.Required()])
    email = TextField('Email:', [validators.Required(), validators.Email(message="Oops! Email address does not exist. Please try again")])
    submit = SubmitField("Sign up for free!")

class login_form(Form):
    username = TextField('Username:', [validators.Required()])
    password = PasswordField('Password:', [validators.Required()])
    submit = SubmitField("Submit")

class forgetpass_form(Form):
    username = TextField('Enter Your Username:', [validators.Required()])
    submit = SubmitField("Submit")

class changepass_form(Form):
    curr_password = PasswordField('Current Password:', [validators.Required()])
    new_password = PasswordField('New Password:', [validators.Required(), validators.EqualTo('confirm', message='Oops! Passwords do not match. Please try again')])
    confirm = PasswordField('Confirm Password:', [validators.Required()])
    submit = SubmitField("Submit")
    
@app.before_request
def load_user():
    if 'user' in session:
        user = session["user"]
    else:
        user = "Guest"
    g.user = user
    
@app.route('/')
def index():
    return render_template('index.html', user=g.user)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/signup', methods=["POST","GET"])
def signup():
    form = signup_form()
    if request.method == 'POST':
##        if form.validate(): #Use wtforms to valid, but not working
        username = request.form['username']
        pw = request.form['password']
        pw_confirm = request.form['confirm']
        email = request.form['email']
        if username == "":
            flash("Oops! Username was not entered")
        elif pw == "" or pw_confirm == "":
            flash("Oops! Password was not entered")
        elif pw != pw_confirm:
            flash("Oops! Passwords do not match")
        elif email == "":
            flash("Oops! Email was not entered")
        elif "@" not in email and "." not in email:
            flash("Oops! This is not an email address")
        else:
            g.db = connect_data()
            cur = g.db.execute('SELECT username FROM users')
            users = [row[0] for row in cur.fetchall()]
            if username in users:
                flash("Oops! This username is already in use.")
            else:
                pw = generate_password_hash(pw)
                g.db.execute('INSERT INTO users (username, password, email) VALUES (?, ?, ?)',
                             [username, pw, email])
                g.db.commit()
                g.db.close()
                message = "You have successfully signed up"
            return render_template('index.html', message=message)
        return render_template('signup.html', form=form)
##        else: # if wtforms validation returns False
##            flash('Oops! Some fields have been left out :(')
##            return render_template('signup.html', form=form)
    elif request.method == 'GET':
        return render_template('signup.html', form=form)
    
@app.route("/log", methods=["GET", "POST"])
def log():
    form = login_form()
    if request.method == 'POST':
##        if form.validate():
        user = request.form['username']
        pw = request.form['password']
        if user == "":
            flash("Oops! Username was not entered")
        elif pw == "":
            flash("Oops! Password was not entered")
        else:
            g.db  = connect_data()
            cur = g.db.execute('SELECT username, password FROM users WHERE username=?', [user])
            valid = [dict(username=row[0], password=row[1]) for row in cur.fetchall()]
            g.db.close()
            for i in valid:
                valid_password = i['password']
            if valid == []:
                flash("Oops! This user has not been registered")
            elif check_password_hash(valid_password, pw):
                session['user'] = user
                session['logged_in'] = True
                message = "You have successfully logged in"
                return render_template('index.html', message=message)
            else:
                flash("Oops! Wrong Password. Please try again")
##        else:
##            flash("Oops! Some fields have been left out :(")
        return render_template("log.html", form=form)
    return render_template("log.html", form=form)

@app.route('/forget', methods=["POST","GET"])
def forget():
    form = forgetpass_form()
    if request.method == 'POST':
##        if form.validate():
        username = request.form['username']
        if username == "":
            flash("Oops! Username was not entered")
        else:
            g.db = connect_data()
            cur = g.db.execute('SELECT username FROM users')
            users = [row[0] for row in cur.fetchall()]
            if username in users:
                cur = g.db.execute('UPDATE users SET password=? WHERE username=?', [generate_password_hash(username), username])
                cur = g.db.execute('SELECT email FROM users WHERE username=?', [username])
                user_email = "%s" % cur.fetchone()
                g.db.commit()
                g.db.close()
##                send_email("[DHS Memento] Reset Password",
##                "memento@dhs.sg",
##                user_email,
##                render_template("forget.txt", user = username))
                message = "Your password has been reset"
            return render_template('index.html', message=message)
##        else:
##            flash('Oops! Some fields have been left out :(')
        return render_template('forget.html', form=form)
    elif request.method == 'GET':
        return render_template('forget.html', form=form)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('user', None)
    return redirect(url_for('index'))

def login_required(test):
    @wraps(test)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return test(*args, **kwargs)
        else:
            flash('Please login to see these pages')
            return redirect(url_for('log'))
    return wrap

@app.route('/browse', methods=['GET', 'POST'])
def browse():
    g.db = connect_db()
    cur = g.db.execute('SELECT name, file, price, quantity FROM merchandise')
    merchandise = [dict(name=row[0], file=row[1], price="{0:.2f}".format(row[2]), quantity=row[3]) for row in cur.fetchall()]
    g.db.close()
    return render_template('browse.html', merchandise = merchandise)

@app.route('/changepass', methods=["POST","GET"])
@login_required
def changepass():
    form = changepass_form()
    if request.method == 'POST':
##        if form.validate():
        curr_password = request.form['curr_password']
        new_password = request.form['new_password']
        confirm = request.form['confirm']
        if curr_password == "":
            flash("Oops! Current password was not entered")
        elif new_password == "" or confirm == "":
            flash("Oops! New password was not entered")
        elif new_password != confirm:
            flash("Oops! Passwords do not match")
        else:
            new_password = generate_password_hash(new_password)
            g.db = connect_data()
            cur = g.db.execute('SELECT password FROM users WHERE username=?', [g.user])
            user_password = "%s" % cur.fetchone()
            if check_password_hash(user_password, curr_password):
                cur = g.db.execute('UPDATE users SET password=? WHERE username=?', [new_password, g.user])
                g.db.commit()
                g.db.close() 
                message = "Your password has been changed"
            return render_template('index.html', message=message)
##        else:
##            flash('Oops! Some fields have been left out :(')
        return render_template('change.html', form=form)
    elif request.method == 'GET':
        return render_template('change.html', form=form)
    
@app.route('/add', methods=['POST'])
@login_required
def new_order():
    g.db = connect_db()
    cur = g.db.execute('SELECT name, file, price, quantity FROM merchandise')
    merchandise = [dict(name=row[0], file=row[1], price="{0:.2f}".format(row[2]), quantity=row[3]) for row in cur.fetchall()]
    g.db.close()
    g.db = connect_data()
    cur = g.db.execute('SELECT item_name FROM orders WHERE confirmed="no" and username=?', [g.user])
    curr_orders = [row[0] for row in cur.fetchall()]
    if request.method == 'POST':
        order = False
        for item in merchandise:
            item_name = item['name']
            price = item['price']
            quantity = int(request.form[item['name']])
            if quantity != 0:
                if item_name in curr_orders:
                    cur = g.db.execute('SELECT quantity FROM orders WHERE confirmed="no" and username=? and item_name=?', [g.user, item_name])
                    prev_quantity = int("%s" % cur.fetchone())
                    new_quantity = quantity + prev_quantity
                    total = float(price) * new_quantity
                    cur = g.db.execute('UPDATE orders SET quantity=?, total=? WHERE confirmed="no" and username=? and item_name=?', [new_quantity, total, g.user, item_name])
                else:
                    total = float(price) * quantity
                    g.db.execute('INSERT INTO orders (username, item_name, price, quantity, total, confirmed) VALUES (?, ?, ?, ?, ?, "no")',
                                 [g.user, item_name, price, quantity, total])
                g.db.commit()
                order = True
        g.db.close()
        if order:
            return redirect(url_for('orders'))
        else:               
            flash("Oops! No orders selected. Please select and submit again.")
            return redirect(url_for('browse'))
    
@app.route('/orders')
@login_required
def orders():
    g.db  = connect_data()
    cur = g.db.execute('SELECT item_name, price, quantity, total FROM orders WHERE confirmed="no" and username=?', [g.user])
    orders = [dict(item_name=row[0], price="{0:.2f}".format(row[1]), quantity=row[2], total="{0:.2f}".format(row[3])) for row in cur.fetchall()]
    grand_total = 0
    if orders == []:
        exists = False
    else:
        exists = True
        for item in orders:
            grand_total = grand_total + float(item['total'])
    g.db.close()
    return render_template('orders.html', orders = orders, grand_total = "{0:.2f}".format(grand_total), exists = exists)

@app.route('/confirm', methods=["POST", "GET"])
@login_required
def confirm():
    g.db  = connect_data()
    cur = g.db.execute('SELECT item_name, price, quantity, total FROM orders WHERE confirmed="no" and username=?', [g.user])
    orders = [dict(item_name=row[0], price="{0:.2f}".format(row[1]), quantity=row[2], total="{0:.2f}".format(row[3])) for row in cur.fetchall()]
    g.db.close()
    grand_total = 0
    if request.method == 'POST':
        for item in orders:
            item_name = item['item_name']
            grand_total = grand_total + float(item['total'])
            quantity = item['quantity']
            g.db = connect_db()
            cur = g.db.execute('SELECT quantity FROM merchandise WHERE name=?', [item_name])
            total_quantity = "%s" % cur.fetchone()
            updated_quantity = int(total_quantity) - int(quantity)
            if updated_quantity > 0:
                cur = g.db.execute('UPDATE merchandise SET quantity=? WHERE name=?', [updated_quantity, item_name])
            else:
                cur = g.db.execute('UPDATE merchandise SET quantity="Out of Stock" WHERE name=?', [item_name])
                flash("Please wait for a restock before going down to collect your items, thank you!")
        g.db.commit()
        g.db.close()
        g.db  = connect_data()
        cur = g.db.execute('UPDATE orders SET confirmed="yes" WHERE username=?', [g.user])
        cur = g.db.execute('SELECT email FROM users WHERE username=?', [g.user])
        user_email = "%s" % cur.fetchone()
        g.db.commit()
        g.db.close()        
##        send_email("[DHS Memento] Thank you for your purchase",
##        "memento@dhs.sg",
##        user_email,
##        render_template("email.txt", user = g.user))
    return render_template('confirmation.html', orders = orders, grand_total = "{0:.2f}".format(grand_total), e=user_email)

@app.route('/edit', methods=["POST", "GET"])
@login_required
def edit():
    g.db  = connect_data()
    cur = g.db.execute('SELECT order_id, item_name, price, quantity, total FROM orders WHERE confirmed="no" and username=?', [g.user])
    orders = [dict(order_id=row[0],item_name=row[1], price="{0:.2f}".format(row[2]), quantity=row[3], total="{0:.2f}".format(row[4])) for row in cur.fetchall()]
    if request.method == 'POST':
        edit = False
        for order in orders:
            if request.form['delete_' + order['item_name']] == 'y':
                cur = g.db.execute('DELETE FROM orders WHERE item_name=? and username=?', [order['item_name'], g.user])
                g.db.commit()
                edit = True
        g.db.close()
        if edit:
            return redirect(url_for('orders'))
        else:
            return redirect(url_for('edit'))
    return render_template('edit.html', orders = orders)
                                   
if __name__ == '__main__':
    app.run(debug=True)
