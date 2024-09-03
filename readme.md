# Hotel Management System

A web-based hotel management system built using Flask, Soft UI for design, and Bootstrap 5.3. This system provides comprehensive management of hotel operations, including client check-ins, services, transactions, room status, user roles, and more.

## Table of Contents

- Features
- Project Structure
- Installation
- Database Models
- Routes
- Technologies Used
- Screenshots
- License

## Features

- **Role-based authentication:** Admin, Manager, and Staff roles with different access levels.
- **Client Management:** Add, edit, check-in, check-out, and view client information.
- **Room Management:** Track room statuses (available, occupied, maintenance) and assign rooms to clients.
- **Service Management:** Add, update, and remove services with categories, including food, massages, room services, etc.
- **Transaction Management:** Monitor and calculate transactions related to rooms, services, and client stays.
- **Income Reporting:** Provides daily, weekly, and monthly income summaries.
- **Password Management:** Managers can generate and send user passwords.

## Project Structure

```plaintext
hotel-management-system/
│
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── routes/
│   │   ├── admin.py
│   │   ├── manager.py
│   │   ├── staff.py
│   │   └── auth.py
│   ├── templates/
│   │   ├── layout.html
│   │   ├── index.html
│   │   ├── manager/
│   │   │   └── dashboard.html
│   │   └── auth/
│   │       └── login.html
│   └── static/
│       └── css/
│           └── style.css
├── config.py
├── requirements.txt
└── README.md
```

## Installation

### Prerequisites
- Python 3.9 and above
- Flask
- A virtual environment (recommended)

### Steps

1. Clone the repository:

```bash
git clone https://github.com/yourusername/hotel-management-system.git
cd hotel-management-system
```

2. Create a virtual environment and activate it:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the dependencies:

```bash
pip install -r requirements.txt
```

4. Set up the database:

```bash
flask shell
from app import db
db.create_all()
exit()
```

5. Run the application:

```bash
flask run
```

6. Access the application at `http://127.0.0.1:5000`

## Database Models

The project includes models for `User`, `Client`, `Room`, `Service`, `Category`, and `Transaction`. Each model has a relationship with the others to manage hotel operations effectively.

## Routes

- **Admin:** Manage users, roles, and high-level hotel operations.
- **Manager:** Oversee day-to-day operations, income reporting, and room/service management.
- **Staff:** Handle client check-ins, service management, and transactions.
- **Auth:** User login, logout, registration, and password management.

## Technologies Used

- **Backend:** Flask, SQLAlchemy
- **Frontend:** Bootstrap 5.3, Soft UI
- **Database:** SQLite (can be upgraded to PostgreSQL or MySQL)

