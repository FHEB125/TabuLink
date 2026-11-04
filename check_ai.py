import sqlite3
conn = sqlite3.connect('db.sqlite3')
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
for r in cur.fetchall():
    name = str(r[0]).lower()
    if 'ai' in name:
        print(r[0])
conn.close()
