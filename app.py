from flask import Flask, render_template, request
import sqlite3
from model import predict_category
from datetime import datetime

app = Flask(__name__)

# DB setup
conn = sqlite3.connect("expense.db")
c = conn.cursor()
c.execute("""
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY,
    description TEXT,
    amount REAL,
    category TEXT,
    date TEXT
)
""")
conn.commit()
conn.close()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        desc = request.form["description"]
        amount = request.form["amount"]
        category = predict_category(desc)
        date = datetime.now().strftime("%Y-%m-%d")

        conn = sqlite3.connect("expense.db")
        c = conn.cursor()
        c.execute("INSERT INTO expenses VALUES (NULL,?,?,?,?)",
                  (desc, amount, category, date))
        conn.commit()
        conn.close()

    conn = sqlite3.connect("expense.db")
    c = conn.cursor()
    c.execute("SELECT category, SUM(amount) FROM expenses GROUP BY category")
    data = c.fetchall()
    conn.close()

    return render_template("index.html", data=data)

if __name__ == "__main__":
    app.run(debug=True)
