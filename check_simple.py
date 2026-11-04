from django.db import connection
conn = connection
cur = conn.cursor()
cur.execute('SELECT name FROM sqlite_master WHERE type=""table""')
for r in cur.fetchall():
    if 'ai' in str(r[0]).lower():
        print(r[0])
