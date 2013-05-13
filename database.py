import sqlite3
import sys

con = sqlite3.connect('merchandise.db')

merchandise = (
    ('A4 lecture pad', 'lecturepad', 2.60, 10),
    ('7-colour sticky note with pen', 'sticky', 4.20, 19),
    ('A5 ring book', 'a5exbook', 4.80, 20),
    ('A5 note book with zip bag', 'a5zipbook', 4.60, 10),
    ('2B pencil', 'pencil', 0.90, 10),
    ('Stainless steel tumbler', 'tumbler', 12.90, 10),
    ('A4 clear holder', 'a4holder', 4.40, 10),
    ('A4 vanguard file', 'a4file', 1.00, 10),
    ('Name card holder', 'cardholder', 10.90, 10),
    ('Umbrella', 'umbrella', 9.00, 10),
    ('School badge (Junior High)', 'jhbadge', 1.30, 10),
    ('School badge (Senior High)', 'shbadge', 1.80, 10),
    ('Dunman dolls (pair)', 'dolls', 45.00, 10)
)

with con:
    cur = con.cursor()
    cur.execute("DROP TABLE IF EXISTS merchandise")
    cur.execute("CREATE TABLE merchandise(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, file TEXT, price INT, quantity INT)")
    cur.executemany("INSERT INTO merchandise(name, file, price, quantity) VALUES(?, ?, ?, ?)", merchandise)
con.close()

con = sqlite3.connect("data.db")
with con:
    cur = con.cursor()
    cur.execute("DROP TABLE IF EXISTS orders")
    cur.execute("CREATE TABLE orders(order_id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, item_name TEXT NOT NULL, price INTEGER NOT NULL, quantity INTEGER NOT NULL, total INTEGER NOT NULL, confirmed TEXT)")
    cur.execute("DROP TABLE IF EXISTS users")
    cur.execute("CREATE TABLE users(user_id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL, password TEXT NOT NULL, email TEXT NOT NULL)")
con.close()

