import sqlite3
import json

conn = sqlite3.connect("app/data/app.db")
cur = conn.cursor()
cols = cur.execute("PRAGMA table_info('tasks')").fetchall()
print(json.dumps(cols, indent=2))
conn.close()
