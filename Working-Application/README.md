# TCS-504 | Assignment 2 — Working System Design Demo

**Course:** B.Tech. CSE · Semester 5  
**Subject:** System Design · **Subject Code:** TCS-504

This runnable educational web application demonstrates all three systems required by the assignment:

1. Food Delivery Application
2. Notification System
3. URL Shortener

## Features

### Food Delivery
- User registration and login
- Browse restaurants and menus
- Add items to cart
- Demo checkout and order creation
- Update and view order delivery status

### Notification System
- Configure Email, SMS, and Push preferences
- Generate notifications for order events
- View notification history and status
- Record a demo retry attempt

### URL Shortener
- Submit a long HTTP/HTTPS URL
- Generate a unique short code
- Redirect to the original URL
- Track clicks for each short link

## Tech stack
- Python + Flask
- SQLite database
- HTML, CSS, Jinja templates

## Run locally (Windows / VS Code)

1. Install Python 3.10 or newer.
2. Extract this ZIP and open the extracted folder in VS Code.
3. Open the VS Code terminal in the project folder.
4. Create a virtual environment:

   ```powershell
   py -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

   If PowerShell blocks activation, use Command Prompt:

   ```bat
   .venv\Scripts\activate.bat
   ```

5. Install dependencies:

   ```bash
   python -m pip install -r requirements.txt
   ```

6. Start the app:

   ```bash
   python app.py
   ```

7. Open **http://127.0.0.1:5000** in your browser.

The SQLite database is created automatically in `instance/project.db`.

## Demo walkthrough
1. Register a user and log in.
2. Open a restaurant, add food to your cart, and place a demo order.
3. Open **My Orders** and change the order status to demonstrate tracking.
4. Open **Notifications** to view notification history and change channel preferences.
5. Open **URL Shortener**, create a link, open the short link, and refresh the page to see its click count increase.

## Important demo limitations
- Checkout is simulated. No real payment is taken.
- Email, SMS, and Push notifications are simulated in the local database. No real messages are sent.
- This is a local educational prototype, not a production-ready service. A public deployment would need stronger security controls, CSRF protection, rate limiting, real provider integrations, tests, and production secret management.
- Do not enter real payment credentials or sensitive personal information.

## Repository structure

```text
TCS504-Assignment-2-Working-Project/
├── app.py
├── requirements.txt
├── README.md
├── ARCHITECTURE.md
├── templates/
└── static/
```
