from flask import Flask, render_template, request, redirect, url_for, session, flash, abort
from werkzeug.security import generate_password_hash, check_password_hash
from urllib.parse import urlparse
import sqlite3
import secrets
import string
from datetime import datetime
from functools import wraps
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-development-secret")
DB_PATH = os.path.join(os.path.dirname(__file__), "instance", "project.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

RESTAURANTS = [
    {"id": 1, "name": "Himalayan Bites", "cuisine": "North Indian", "items": [
        {"id": 1, "name": "Paneer Thali", "price": 180},
        {"id": 2, "name": "Veg Biryani", "price": 150},
        {"id": 3, "name": "Dal Makhani", "price": 130},
    ]},
    {"id": 2, "name": "Campus Cafe", "cuisine": "Cafe & Snacks", "items": [
        {"id": 4, "name": "Veg Burger", "price": 90},
        {"id": 5, "name": "Cheese Sandwich", "price": 110},
        {"id": 6, "name": "Cold Coffee", "price": 80},
    ]},
    {"id": 3, "name": "Green Bowl", "cuisine": "Healthy Food", "items": [
        {"id": 7, "name": "Veg Salad Bowl", "price": 120},
        {"id": 8, "name": "Grilled Paneer Bowl", "price": 170},
    ]},
]

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    with get_db() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email_enabled INTEGER DEFAULT 1,
            sms_enabled INTEGER DEFAULT 1,
            push_enabled INTEGER DEFAULT 1
        );
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            restaurant_name TEXT NOT NULL,
            items TEXT NOT NULL,
            total REAL NOT NULL,
            status TEXT NOT NULL DEFAULT 'PLACED',
            payment_status TEXT NOT NULL DEFAULT 'PAID',
            created_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            channel TEXT NOT NULL,
            category TEXT NOT NULL,
            message TEXT NOT NULL,
            status TEXT NOT NULL,
            attempts INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
        CREATE TABLE IF NOT EXISTS short_urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            code TEXT UNIQUE NOT NULL,
            long_url TEXT NOT NULL,
            clicks INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
        """)
init_db()

def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in first.", "warning")
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped

def current_user():
    if "user_id" not in session:
        return None
    with get_db() as db:
        return db.execute("SELECT * FROM users WHERE id=?", (session["user_id"],)).fetchone()

def send_notification(user_id, category, message):
    """Local demo: records enabled channels in the database; no real SMS/email is sent."""
    with get_db() as db:
        user = db.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
        if not user:
            return
        channels = []
        if user["email_enabled"]:
            channels.append("Email (simulated)")
        if user["sms_enabled"]:
            channels.append("SMS (simulated)")
        if user["push_enabled"]:
            channels.append("Push (simulated)")
        for channel in channels:
            db.execute(
                """INSERT INTO notifications
                   (user_id, channel, category, message, status, attempts, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (user_id, channel, category, message, "SENT (demo)", 1, datetime.now().strftime("%Y-%m-%d %H:%M"))
            )

@app.context_processor
def inject_user():
    return {"logged_in_user": current_user(), "year": datetime.now().year}

@app.route("/")
def index():
    return render_template("index.html", restaurants=RESTAURANTS)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        if not name or not email or len(password) < 6:
            flash("Enter your name, a valid email, and a password of at least 6 characters.", "danger")
            return render_template("register.html")
        try:
            with get_db() as db:
                db.execute("INSERT INTO users (name,email,password_hash) VALUES (?,?,?)",
                           (name, email, generate_password_hash(password)))
            flash("Account created. You can now log in.", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("An account with this email already exists.", "danger")
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        with get_db() as db:
            user = db.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        if user and check_password_hash(user["password_hash"], password):
            session.clear()
            session["user_id"] = user["id"]
            flash("Welcome back!", "success")
            return redirect(url_for("index"))
        flash("Incorrect email or password.", "danger")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("index"))

@app.route("/restaurant/<int:restaurant_id>")
def restaurant(restaurant_id):
    selected = next((r for r in RESTAURANTS if r["id"] == restaurant_id), None)
    if not selected:
        abort(404)
    return render_template("restaurant.html", restaurant=selected)

@app.route("/cart/add/<int:item_id>", methods=["POST"])
@login_required
def add_to_cart(item_id):
    item = next((item for r in RESTAURANTS for item in r["items"] if item["id"] == item_id), None)
    if not item:
        abort(404)
    cart = session.get("cart", {})
    cart[str(item_id)] = int(cart.get(str(item_id), 0)) + 1
    session["cart"] = cart
    flash(item["name"] + " added to cart.", "success")
    return redirect(request.referrer or url_for("index"))

def cart_details():
    cart = session.get("cart", {})
    rows = []
    total = 0
    for restaurant in RESTAURANTS:
        for item in restaurant["items"]:
            qty = int(cart.get(str(item["id"]), 0))
            if qty:
                subtotal = qty * item["price"]
                rows.append({"item": item, "restaurant": restaurant["name"], "qty": qty, "subtotal": subtotal})
                total += subtotal
    return rows, total

@app.route("/cart")
@login_required
def cart():
    rows, total = cart_details()
    return render_template("cart.html", rows=rows, total=total)

@app.route("/cart/remove/<int:item_id>", methods=["POST"])
@login_required
def remove_from_cart(item_id):
    cart_data = session.get("cart", {})
    cart_data.pop(str(item_id), None)
    session["cart"] = cart_data
    return redirect(url_for("cart"))

@app.route("/checkout", methods=["POST"])
@login_required
def checkout():
    rows, total = cart_details()
    if not rows:
        flash("Your cart is empty.", "warning")
        return redirect(url_for("cart"))
    restaurant_names = {row["restaurant"] for row in rows}
    if len(restaurant_names) > 1:
        flash("For this demo, please order from one restaurant at a time.", "warning")
        return redirect(url_for("cart"))
    summary = ", ".join(f'{r["item"]["name"]} x {r["qty"]}' for r in rows)
    restaurant_name = rows[0]["restaurant"]
    with get_db() as db:
        cur = db.execute(
            """INSERT INTO orders (user_id,restaurant_name,items,total,status,payment_status,created_at)
               VALUES (?,?,?,?,?,?,?)""",
            (session["user_id"], restaurant_name, summary, total, "PLACED", "PAID (demo)",
             datetime.now().strftime("%Y-%m-%d %H:%M"))
        )
        order_id = cur.lastrowid
    session["cart"] = {}
    send_notification(session["user_id"], "Order update", f"Order #{order_id} placed successfully.")
    flash("Demo payment successful and order placed!", "success")
    return redirect(url_for("orders"))

@app.route("/orders")
@login_required
def orders():
    with get_db() as db:
        rows = db.execute("SELECT * FROM orders WHERE user_id=? ORDER BY id DESC", (session["user_id"],)).fetchall()
    return render_template("orders.html", orders=rows)

@app.route("/order/<int:order_id>/status", methods=["POST"])
@login_required
def update_order_status(order_id):
    allowed = ["PLACED", "PREPARING", "OUT FOR DELIVERY", "DELIVERED"]
    status = request.form.get("status")
    if status not in allowed:
        abort(400)
    with get_db() as db:
        order = db.execute("SELECT * FROM orders WHERE id=? AND user_id=?", (order_id, session["user_id"])).fetchone()
        if not order:
            abort(404)
        db.execute("UPDATE orders SET status=? WHERE id=?", (status, order_id))
    send_notification(session["user_id"], "Order update", f"Order #{order_id} status changed to {status}.")
    flash("Order status updated (demo).", "success")
    return redirect(url_for("orders"))

@app.route("/notifications", methods=["GET", "POST"])
@login_required
def notifications():
    if request.method == "POST":
        with get_db() as db:
            db.execute("""UPDATE users SET email_enabled=?, sms_enabled=?, push_enabled=? WHERE id=?""",
                       (1 if request.form.get("email") else 0,
                        1 if request.form.get("sms") else 0,
                        1 if request.form.get("push") else 0,
                        session["user_id"]))
        flash("Notification preferences saved.", "success")
        return redirect(url_for("notifications"))
    with get_db() as db:
        user = db.execute("SELECT * FROM users WHERE id=?", (session["user_id"],)).fetchone()
        history = db.execute("SELECT * FROM notifications WHERE user_id=? ORDER BY id DESC LIMIT 50",
                             (session["user_id"],)).fetchall()
    return render_template("notifications.html", user=user, history=history)

@app.route("/notifications/retry/<int:notification_id>", methods=["POST"])
@login_required
def retry_notification(notification_id):
    with get_db() as db:
        notification = db.execute("SELECT * FROM notifications WHERE id=? AND user_id=?",
                                  (notification_id, session["user_id"])).fetchone()
        if not notification:
            abort(404)
        db.execute("UPDATE notifications SET attempts=attempts+1, status=? WHERE id=?",
                   ("RETRIED (demo)", notification_id))
    flash("Demo retry recorded. No real message was sent.", "info")
    return redirect(url_for("notifications"))

def make_code(length=6):
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))

@app.route("/shortener", methods=["GET", "POST"])
@login_required
def shortener():
    if request.method == "POST":
        long_url = request.form.get("long_url", "").strip()
        parsed = urlparse(long_url)
        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            flash("Enter a complete URL beginning with http:// or https://", "danger")
            return redirect(url_for("shortener"))
        with get_db() as db:
            code = make_code()
            while db.execute("SELECT 1 FROM short_urls WHERE code=?", (code,)).fetchone():
                code = make_code()
            db.execute("INSERT INTO short_urls (user_id,code,long_url,created_at) VALUES (?,?,?,?)",
                       (session["user_id"], code, long_url,
                        datetime.now().strftime("%Y-%m-%d %H:%M")))
        flash("Short URL created.", "success")
        return redirect(url_for("shortener"))
    with get_db() as db:
        links = db.execute("SELECT * FROM short_urls WHERE user_id=? ORDER BY id DESC",
                           (session["user_id"],)).fetchall()
    return render_template("shortener.html", links=links)

@app.route("/s/<code>")
def follow_short_url(code):
    with get_db() as db:
        link = db.execute("SELECT * FROM short_urls WHERE code=?", (code,)).fetchone()
        if not link:
            abort(404)
        db.execute("UPDATE short_urls SET clicks=clicks+1 WHERE id=?", (link["id"],))
    return redirect(link["long_url"], code=302)

@app.errorhandler(404)
def not_found(error):
    return render_template("404.html"), 404

if __name__ == "__main__":
    app.run(debug=True)
