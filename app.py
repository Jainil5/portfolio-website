import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector

app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests

# --- DATABASE CONFIGURATION ---
# IMPORTANT: Replace these with your actual Hostinger MariaDB/MySQL credentials.
# You can find these details in your Hostinger hPanel under "Databases" -> "MySQL Databases".
DB_HOST = "your_database_host"   # e.g., "127.0.0.1" or a specific hostname
DB_USER = "your_database_user"   # e.g., "u123456789_user"
DB_PASSWORD = "your_database_password" # e.g., "my_secure_password"
DB_NAME = "your_database_name"   # e.g., "u123456789_database"

def get_db_connection():
    """Establishes a connection to the MariaDB database."""
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        return conn
    except mysql.connector.Error as err:
        print(f"Error connecting to the database: {err}")
        return None

def setup_database():
    """
    Creates the 'appointments' table with a timestamp column if it doesn't exist.
    """
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            # SQL to create the table with new columns for email and message
            create_table_query = """
            CREATE TABLE IF NOT EXISTS appointments (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                mobile_number VARCHAR(20) NOT NULL,
                email VARCHAR(255) NOT NULL,
                message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
            cursor.execute(create_table_query)
            conn.commit()
            print("Database table 'appointments' is ready.")
        except mysql.connector.Error as err:
            print(f"Error creating table: {err}")
        finally:
            cursor.close()
            conn.close()

# Call this function once when you're setting up the app to create the table
setup_database()

@app.route('/api/book_appointment', methods=['POST'])
def book_appointment():
    """
    API endpoint to receive appointment booking data.
    - Receives JSON data from the frontend.
    - Inserts the data into the 'appointments' table, including email and message.
    - The created_at field is automatically populated by the database.
    - Returns a JSON response.
    """
    try:
        data = request.json
        name = data.get('name')
        mobile_number = data.get('phone') # Changed to 'phone' to match new HTML
        email = data.get('email')
        message = data.get('message')

        # Basic data validation for required fields
        if not all([name, mobile_number, email]):
            return jsonify({"status": "error", "message": "Name, mobile number, and email are required."}), 400

        conn = get_db_connection()
        if conn is None:
            return jsonify({"status": "error", "message": "Could not connect to the database."}), 500

        cursor = conn.cursor()
        
        # SQL query to insert data into the table
        insert_query = """
        INSERT INTO appointments (name, mobile_number, email, message)
        VALUES (%s, %s, %s, %s);
        """
        appointment_data = (name, mobile_number, email, message)
        
        cursor.execute(insert_query, appointment_data)
        conn.commit()

        return jsonify({"status": "success", "message": "Appointment booked successfully!"}), 200

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"status": "error", "message": "An internal server error occurred."}), 500
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn:
            conn.close()

if __name__ == '__main__':
    # When running on your local machine for development
    app.run(debug=True)
