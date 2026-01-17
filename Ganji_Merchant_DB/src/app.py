from flask import Flask, render_template_string, request, redirect
from urllib.parse import quote
from engine import Database
import datetime

app = Flask(__name__)

# Initialize DB (Path is handled automatically by engine now)
db = Database()

# === TRANSLATION LAYER ===
def translate_message(raw_msg):
    msg_lower = raw_msg.lower()
    if "inserted" in msg_lower or "success" in msg_lower or "saved" in msg_lower or "created" in msg_lower:
        return "Operation successful!", "success"
    if "duplicate" in msg_lower:
        return "⚠️ Payment Failed: Transaction ID collision.", "error"
    elif "type error" in msg_lower:
        return "⚠️ Input Error: 'Amount' must be a number.", "error"
    elif "mismatch" in msg_lower:
        return "⚠️ Data Error: Please ensure all fields are filled.", "error"
    elif "exists" in msg_lower and "table" in msg_lower:
        return "System Notification: The database is already active.", "warning"
    else:
        return f"System Error: {raw_msg}", "error"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Ganji Merchant Portal</title>
    <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>💰</text></svg>">
    
    <style>
        :root { --primary: #008CBA; --bg: #f4f7f6; --text: #333; }
        body { font-family: 'Segoe UI', sans-serif; background-color: var(--bg); color: var(--text); max-width: 900px; margin: 0 auto; padding: 20px; display: flex; flex-direction: column; min-height: 95vh; }
        .content-wrap { flex: 1; }
        .header { text-align: center; margin-bottom: 30px; }
        .tagline { color: #666; font-style: italic; margin-top: -15px; font-size: 14px; }
        .card { background: white; padding: 25px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 20px; }
        h1 { color: var(--primary); margin-bottom: 5px; }
        h3 { border-bottom: 2px solid var(--primary); padding-bottom: 10px; margin-top: 0; }
        input, select { width: 100%; padding: 12px; margin: 8px 0; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; transition: border 0.3s; }
        input:focus, select:focus { border-color: var(--primary); outline: none; box-shadow: 0 0 5px rgba(0, 140, 186, 0.2); }
        input:focus:invalid { border-color: #dc3545; box-shadow: 0 0 5px rgba(220, 53, 69, 0.2); }
        button { background-color: var(--primary); color: white; padding: 12px; border: none; border-radius: 4px; cursor: pointer; width: 100%; font-size: 16px; font-weight: bold; transition: background 0.3s; }
        button:hover { background-color: #007bb5; }
        .btn-reset { background-color: #607D8B; margin-bottom: 15px; width: auto; font-size: 14px; padding: 8px 16px;}
        .btn-reset:hover { background-color: #455A64; }
        table { width: 100%; border-collapse: collapse; margin-top: 15px; }
        th, td { text-align: left; padding: 12px; border-bottom: 1px solid #ddd; }
        th { background-color: var(--primary); color: white; }
        tr:hover { background-color: #f1f1f1; }
        .footer { text-align: center; margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; color: #888; font-size: 13px; }
        .footer span { color: var(--primary); font-weight: bold; }
        #toast-container { visibility: hidden; min-width: 300px; background-color: #333; color: #fff; text-align: left; border-radius: 8px; padding: 20px; position: fixed; z-index: 1000; right: 30px; top: 30px; font-size: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.2); opacity: 0; transform: translateY(-20px); transition: all 0.5s ease; cursor: pointer; display: flex; align-items: center; }
        #toast-container.show { visibility: visible; opacity: 1; transform: translateY(0); }
        .toast-success { background-color: #fff !important; color: #2e7d32 !important; border-left: 8px solid #2e7d32; }
        .toast-error { background-color: #fff !important; color: #c62828 !important; border-left: 8px solid #c62828; }
        .toast-icon { font-size: 20px; margin-right: 15px; }
    </style>
</head>
<body>
    <div id="toast-container" onclick="hideToast()">
        <span id="toast-icon" class="toast-icon"></span>
        <span id="toast-message"></span>
    </div>

    <div class="content-wrap">
        <div class="header">
            <h1>GANJI MERCHANT PORTAL</h1>
            <p class="tagline">Empowering Kenyan SMEs, One Transaction at a Time.</p>
        </div>

        <div class="card">
            <h3>💰 Record New Sale</h3>
            <form action="/add" method="post">
                <label style="font-size: 14px; color: #666;">Transaction Details</label>
                <div style="display: flex; gap: 10px;">
                    <input type="number" name="amount" placeholder="Amount (KES)" required min="0.01" step="0.01">
                </div>
                <input type="text" name="customer" placeholder="Customer Name" required>
                <select name="method">
                    <option value="M-PESA">M-PESA</option>
                    <option value="CARD">Visa/Mastercard</option>
                    <option value="CASH">Cash</option>
                </select>
                <button type="submit">Process Transaction</button>
            </form>
        </div>

        <div class="card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <h3>📊 Sales Ledger</h3>
                <form action="/setup" method="post" style="margin: 0;">
                    <button type="submit" class="btn-reset">⚠️ Reset Database</button>
                </form>
            </div>
            <table>
                <thead>
                    <tr><th>TxID</th><th>Customer</th><th>Amount (KES)</th><th>Method</th></tr>
                </thead>
                <tbody>
                    {% for row in rows %}
                    <tr>
                        <td><span style="background: #eee; padding: 2px 6px; border-radius: 4px; font-family: monospace;">#{{ row['id'] }}</span></td>
                        <td>{{ row['customer'] }}</td>
                        <td>Ksh {{ row['amount'] }}</td>
                        <td>{{ row['method'] }}</td>
                    </tr>
                    {% else %}
                    <tr><td colspan="4" style="text-align:center; color: #999;">No transactions found.</td></tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>

    <div class="footer">
        <p>&copy; {{ year }} Ganji Systems Ltd. All Rights Reserved.</p>
        <p>Built for the <span>Pesapal Junior Dev Challenge '26</span> by <a href="https://ray.paymentsoverflow.com" target="_blank"><span>Ray Basweti</span></a></p>
    </div>

    <script>
        const msg = "{{ msg }}";
        const type = "{{ msg_type }}";
        const toast = document.getElementById("toast-container");
        const toastMsg = document.getElementById("toast-message");
        const toastIcon = document.getElementById("toast-icon");

        function showToast() {
            if (!msg) return;
            toastMsg.innerText = msg;
            if (type === 'success') { toast.classList.add("toast-success"); toastIcon.innerText = "✅"; } 
            else { toast.classList.add("toast-error"); toastIcon.innerText = "🚫"; }
            setTimeout(() => { toast.classList.add("show"); }, 100);
            setTimeout(hideToast, 5000);
            if (window.history.replaceState) {
                const url = new URL(window.location);
                url.searchParams.delete('msg');
                url.searchParams.delete('type');
                window.history.replaceState(null, '', url);
            }
        }
        function hideToast() { toast.classList.remove("show"); }
        showToast();
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    msg = request.args.get("msg", "")
    msg_type = request.args.get("type", "")
    current_year = datetime.datetime.now().year
    
    # === SYNC FIX: LOAD FRESH DATA ===
    # Before we render the page, check the file for any updates from the REPL
    db.load_from_disk()
    
    rows = []
    try:
        if "sales" in db.tables:
            result = db.execute_query("SELECT * FROM sales")
            if isinstance(result, list):
                # Reverse the list so newest transactions appear first!
                rows = result[::-1] 
    except:
        pass
        
    return render_template_string(HTML_TEMPLATE, rows=rows, msg=msg, msg_type=msg_type, year=current_year)

@app.route("/setup", methods=["POST"])
def setup():
    try:
        if "sales" in db.tables: del db.tables["sales"]
        db.execute_query("CREATE TABLE sales (id int, customer str, amount float, method str) PK id")
        db.execute_query("INSERT INTO sales VALUES (1001, John_Kamau, 1500.50, M-PESA)")
        db.execute_query("INSERT INTO sales VALUES (1002, Alice_Wambui, 4500.00, CARD)")
        db.save_to_disk()
        msg = quote("System successfully initialized!")
        return redirect(f"/?msg={msg}&type=success")
    except Exception as e:
        user_msg, type_msg = translate_message(str(e))
        return redirect(f"/?msg={quote(user_msg)}&type={type_msg}")

@app.route("/add", methods=["POST"])
def add_transaction():
    # === SYNC FIX: LOAD BEFORE ADDING ===
    # Ensure we have the latest collision data
    db.load_from_disk()

    customer = request.form["customer"].replace(" ", "_")
    amount = request.form["amount"]
    method = request.form["method"]
    
    res = db.execute_query(f"INSERT INTO sales VALUES (AUTO, {customer}, {amount}, {method})")
    db.save_to_disk()
    
    user_msg, type_msg = translate_message(str(res))
    if type_msg == "success":
        try:
            generated_id = str(res).split("ID:")[1].strip()
            user_msg = f"Transaction #{generated_id} Recorded Successfully! ✅"
        except:
            user_msg = "Transaction Recorded Successfully! ✅"
    
    return redirect(f"/?msg={quote(user_msg)}&type={type_msg}")

if __name__ == "__main__":
    app.run(debug=True, port=5000)