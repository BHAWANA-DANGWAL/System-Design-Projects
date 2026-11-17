# TCS-504 — Assignment 2: System Design

This repository contains the original High-Level Design (HLD) documentation and an educational working prototype for the three systems in the supplied assignment brief.

## Assignment deliverables — HLD documentation

The assignment asks for a simple HLD for:
1. **Food Delivery System**
2. **Notification System**
3. **URL Shortener**

The original HLD PDFs are preserved in [`HLD-Documentation/`](HLD-Documentation/).

## Additional practical implementation

The [`Working-Application/`](Working-Application/) folder contains a Flask + SQLite web application demonstrating the three concepts:

- Food delivery: registration/login, restaurant menus, cart, demo checkout, and order status tracking.
- Notification system: channel preferences, notification history, and simulated retry.
- URL shortener: short-link generation, redirection, and click counting.

## Repository structure

```text
TCS504-Assignment-2/
├── README.md
├── HLD-Documentation/
│   ├── Q1_Food_Delivery_System_HLD.pdf
│   ├── Q2_Notification_System_HLD.pdf
│   └── Q3_URL_Shortener_HLD.pdf
└── Working-Application/
    ├── app.py
    ├── requirements.txt
    ├── README.md
    ├── ARCHITECTURE.md
    ├── templates/
    └── static/
```

## Run the working application

1. Open `Working-Application` in VS Code.
2. Create and activate a virtual environment.
3. Install dependencies using `pip install -r requirements.txt`.
4. Run `python app.py`.
5. Open `http://127.0.0.1:5000`.

See [`Working-Application/README.md`](Working-Application/README.md) for detailed Windows instructions.

## Important scope note

The assignment deliverable is the HLD documentation. The Flask application is an additional educational demonstration, not a replacement for the HLDs. Payment and Email/SMS/Push delivery are simulated; no real payment or messages are processed. This prototype is intended for local learning and is not production-ready.
