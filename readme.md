# CSV Data Processing API

This project is a simple backend API that handles CSV file uploads, data ingestion, and basic data processing. It provides secure endpoints for uploading CSV files, storing data, and retrieving summary statistics.

## Features

- RESTful API with endpoints for user authentication, CSV upload, and data retrieval
- Basic validation for uploaded CSV files
- Data storage in MySQL database
- Simple data processing to calculate summary statistics
- Secure endpoints with JWT authentication

## Prerequisites

- Python 3.7+
- MySQL Server
- Virtual environment tool (e.g., venv, virtualenv)

## Setup

1. Clone the repository:
2. Create and activate a virtual environment:
python -m venv venv
source venv/bin/activate  # On Windows, use venv\Scripts\activate
3. Install dependencies:pip install -r requirements.txt
4. Set up the MySQL database:
- Create a database named `read_csv`
- Update the database URL in `/database/data.py` with your MySQL credentials

5. Create the required tables in the `read_csv` database:
```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL
);

CREATE TABLE your_data (
    pri_key INT AUTO_INCREMENT PRIMARY KEY,
    id INT,
    document_id int,
    username VARCHAR(50),
    email VARCHAR(100),
    path VARCHAR(255) DEFAULT NULL,
    FOREIGN KEY (id) REFERENCES users(id)
);


uvicorn main:app --reload
Access the API documentation at http://localhost:8000/docs

Usage

For first-time users, use the signup endpoint to create an account.
Log in using your credentials to receive a JWT token.
Use the JWT token to authenticate and access the CSV-related endpoints.

API Endpoints

/signup: Create a new user account
/login: Authenticate and receive a JWT token
/upload-csv: Upload and process a CSV file (requires authentication)
/document-stats/: Retrieve summary statistics for uploaded data (requires authentication)

Security

Endpoints are secured with JWT authentication
Basic input validation is implemented



