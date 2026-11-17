# Architecture overview

This is a single Flask application with three modules matching the assignment.

- **Food delivery:** Flask routes, a Python menu catalogue, and SQLite users/orders tables. Checkout and payment are simulated.
- **Notifications:** SQLite stores user channel preferences and notification history. Email, SMS, and Push are simulated records.
- **URL shortener:** SQLite stores unique short-code mappings. The `/s/<code>` route redirects and increments the click count.

SQLite is created automatically, so no separate database server is required.
