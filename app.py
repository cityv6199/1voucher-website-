from flask import Flask, request, render_template, jsonify
import sqlite3

app = Flask(__name__)

# Database Initialization
def init_db():
    conn = sqlite3.connect('vouchers.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS vouchers (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        voucher_number TEXT UNIQUE NOT NULL,
                        status TEXT DEFAULT 'active'
                      )''')
    # Sample data
    cursor.execute("INSERT OR IGNORE INTO vouchers (voucher_number, status) VALUES ('12345ABCDE', 'active')")
    cursor.execute("INSERT OR IGNORE INTO vouchers (voucher_number, status) VALUES ('67890FGHIJ', 'active')")
    conn.commit()
    conn.close()

# Verify Voucher
def verify_voucher(voucher_number):
    conn = sqlite3.connect('vouchers.db')
    cursor = conn.cursor()
    cursor.execute("SELECT status FROM vouchers WHERE voucher_number = ?", (voucher_number,))
    result = cursor.fetchone()
    conn.close()
    return result

# Update Voucher Status
def update_voucher_status(voucher_number):
    conn = sqlite3.connect('vouchers.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE vouchers SET status = 'claimed' WHERE voucher_number = ?", (voucher_number,))
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/claim', methods=['POST'])
def claim_voucher():
    data = request.json
    voucher_number = data.get('voucherNumber')

    if not voucher_number:
        return jsonify({"status": "error", "message": "Voucher number is required."}), 400

    voucher = verify_voucher(voucher_number)
    if voucher:
        if voucher[0] == 'active':
            update_voucher_status(voucher_number)
            return jsonify({"status": "success", "message": "Voucher claimed successfully!"})
        else:
            return jsonify({"status": "error", "message": "Voucher already claimed."}), 400
    else:
        return jsonify({"status": "error", "message": "Invalid voucher number."}), 400

if __name__ == '__main__':
    init_db()
    app.run(debug=True)