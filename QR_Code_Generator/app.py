from flask import Flask, render_template, request, send_file
import sqlite3
import qrcode
import io
import base64
from fpdf import FPDF

app = Flask(__name__)

def create_tables():
    """Create all tables for db."""
    conn = sqlite3.connect("qr_codes.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
        First_Name TEXT NOT NULL,
        Last_Name TEXT NOT NULL,
        Address TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        product_id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        order_date DATE NOT NULL,
        description TEXT NOT NULL,
        FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS qr_codes (
        qr_id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER,
        description TEXT NOT NULL,
        qr_code TEXT NOT NULL,
        FOREIGN KEY (product_id) REFERENCES products (product_id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS locations (
        location_id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER,
        description TEXT NOT NULL,
        FOREIGN KEY (product_id) REFERENCES products (product_id)
    )
    """)
    conn.commit()
    conn.close()

@app.route("/", methods=["GET", "POST"])
def index():
    # Check, if Formular has been sent
    if request.method == "POST":
        # Call Values of Formular
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        address = request.form["address"]
        order_date = request.form["order_date"]
        product_description = request.form["product_description"]
        qr_description = request.form["qr_description"]
        location_description = request.form["location_description"]

        # Connection to Database
        conn = sqlite3.connect("qr_codes.db")
        cursor = conn.cursor()

        # Insert the inserted Data for Customer in Table customers
        cursor.execute("INSERT INTO customers (First_Name, Last_Name, Address) VALUES (?, ?, ?)", #insert Data in customers
                       (first_name, last_name, address))
        customer_id = cursor.lastrowid

        # Insert the inserted Data for Product in Table products
        cursor.execute("INSERT INTO products (customer_id, order_date, description) VALUES (?, ?, ?)", #insert Data in products
                            (customer_id, order_date, product_description))
        product_id = cursor.lastrowid

        # Insert the inserted Data for QR-Code in Table qr_codes
        cursor.execute("INSERT INTO qr_codes (product_id, description, qr_code) VALUES (?, ?, ?)", #insert Data in qr_codes
                    (product_id, qr_description, ''))

        # Insert the inserted Data for Location in Table locations
        cursor.execute("INSERT INTO locations (product_id, description) VALUES (?, ?)", #insert Data in locations
                       (product_id, location_description))

        qr_id = cursor.lastrowid # call qr_id

        # Create QR-Code with QRCode-Library
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
        qr.add_data(qr_description)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        # Save images of QR-Code
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        qr_code_base64 = base64.b64encode(buf.getvalue()).decode("utf-8")

        cursor.execute("UPDATE qr_codes SET qr_code = ? WHERE qr_id = ?", (qr_code_base64, qr_id))

        conn.commit()
        conn.close()

        return render_template("index.html", qr_code_base64=qr_code_base64)

    return render_template("index.html")

if __name__ == "__main__":
    create_tables()
    app.run(debug=True)
