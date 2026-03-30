import sqlite3
conn = sqlite3.connect('data/aivi_index.db')
rows = conn.execute("SELECT website_url FROM practices WHERE name LIKE '%Cornerstone%' AND city='Charlotte'").fetchall()
for r in rows:
    print(r[0])
