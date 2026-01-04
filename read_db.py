import sqlite3

def read_payments():
    conn = sqlite3.connect("payment.db")
    cursor = conn.cursor()

    # cursor.execute("SELECT id, payment_uid, status FROM payments")
    cursor.execute("SELECT * FROM payments")
    rows = cursor.fetchall()

    print("\n--- Payments in Database ---")
    for row in rows:
        print(row)

    conn.close()

if __name__ == "__main__":
    read_payments()
