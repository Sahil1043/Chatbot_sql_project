import sqlite3
from pathlib import Path

# Function to create SQLite database connection
def create_connection(db_file):
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        print(e)
    return None

# Function to create tables and insert dummy data
def create_tables(conn):
    try:
        cursor = conn.cursor()

        # Create Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL
            )
        ''')

        # Create Products table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Products (
                product_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(255) NOT NULL,
                price DECIMAL(10, 2) NOT NULL,
                stock_quantity INT NOT NULL DEFAULT 0
            )
        ''')

        # Create Orders table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Orders (
                order_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INT,
                order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT CHECK(status IN ('pending', 'shipped', 'delivered')) DEFAULT 'pending',
                FOREIGN KEY (user_id) REFERENCES Users(user_id)
            )
        ''')

        # Create Order_Items table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Order_Items (
                order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INT,
                product_id INT,
                quantity INT NOT NULL,
                price DECIMAL(10, 2) NOT NULL,
                FOREIGN KEY (order_id) REFERENCES Orders(order_id),
                FOREIGN KEY (product_id) REFERENCES Products(product_id)
            )
        ''')

        # Create Categories table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Categories (
                category_id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_name VARCHAR(100) NOT NULL
            )
        ''')

        # Insert dummy data into Users table
        cursor.executemany('''
            INSERT INTO Users (name, email) VALUES (?, ?)
        ''', [
            ('John Doe', 'john.doe@example.com'),
            ('Jane Smith', 'jane.smith@example.com'),
            ('Mike Johnson', 'mike.johnson@example.com')
        ])

        # Insert dummy data into Products table
        cursor.executemany('''
            INSERT INTO Products (name, price, stock_quantity) VALUES (?, ?, ?)
        ''', [
            ('Product A', 19.99, 100),
            ('Product B', 29.99, 50),
            ('Product C', 39.99, 75)
        ])

        # Insert dummy data into Orders table
        cursor.executemany('''
            INSERT INTO Orders (user_id, order_date, status) VALUES (?, CURRENT_TIMESTAMP, ?)
        ''', [
            (1, 'pending'),
            (2, 'shipped'),
            (3, 'delivered')
        ])

        # Insert dummy data into Order_Items table
        cursor.executemany('''
            INSERT INTO Order_Items (order_id, product_id, quantity, price) VALUES (?, ?, ?, ?)
        ''', [
            (1, 1, 2, 39.98),
            (2, 2, 1, 29.99),
            (3, 3, 3, 119.97)
        ])

        # Insert dummy data into Categories table
        cursor.executemany('''
            INSERT INTO Categories (category_name) VALUES (?)
        ''', [
            ('Category 1',),
            ('Category 2',),
            ('Category 3',)
        ])

        conn.commit()
        cursor.close()
        print("Tables created and data inserted successfully.")

    except sqlite3.Error as e:
        print(f"Error: {e}")

def get_order_details(conn, email):
    try:
        cursor = conn.cursor()

        # Retrieve user details based on email
        cursor.execute('''
            SELECT user_id, name FROM Users WHERE email = ?
        ''', (email,))
        user = cursor.fetchone()

        if user:
            user_id, name = user
            # Retrieve orders for the user
            cursor.execute('''
                SELECT order_id, order_date, status FROM Orders WHERE user_id = ?
            ''', (user_id,))
            orders = cursor.fetchall()

            # Print user details and orders
            print(f"User: {name} ({email})")
            print("Orders:")
            for order in orders:
                order_id, order_date, status = order
                print(f"  Order ID: {order_id}, Date: {order_date}, Status: {status}")
        else:
            print("Invalid credentials: User not found.")

        cursor.close()

    except sqlite3.Error as e:
        print(f"Error: {e}")

def get_order_status(conn, identifier):
    try:
        cursor = conn.cursor()

        # Check if identifier is an email or order ID
        cursor.execute('''
            SELECT user_id, name FROM Users WHERE email = ? OR user_id = ?
        ''', (identifier, identifier))
        user = cursor.fetchone()

        if user:
            user_id, name = user
            # Retrieve order status for the user
            cursor.execute('''
                SELECT order_id, status FROM Orders WHERE user_id = ? OR order_id = ?
            ''', (user_id, identifier))
            orders = cursor.fetchall()

            # Print user name and order statuses
            print(f"User: {name}")
            print("Order Statuses:")
            for order in orders:
                order_id, status = order
                print(f"  Order ID: {order_id}, Status: {status}")
        else:
            print("Invalid credentials: User or order not found.")

        cursor.close()

    except sqlite3.Error as e:
        print(f"Error: {e}")

def chatbot_main(conn):
    print("Hi there! How can I help you?")
    print("1. Get order Details (Enter email)")
    print("2. Get order Status (Enter email or order ID)")

    while True:
        choice = input(">> ")

        if choice == '1':
            email = input("Enter email: ")
            get_order_details(conn, email)
        elif choice == '2':
            identifier = input("Enter email or order ID: ")
            get_order_status(conn, identifier)
        else:
            print("Invalid choice. Please choose 1 or 2.")

        another_query = input("Do you want to perform another query? (yes/no): ")
        if another_query.lower() != 'yes':
            break

    print("Exiting chatbot.")

# Main function
def main():
    database_file = Path.cwd() / 'mydatabase.db'  # SQLite database file path
    conn = create_connection(str(database_file))  # Connect to SQLite database

    if conn is not None:
        create_tables(conn)  # Create tables and insert data
        chatbot_main(conn)  # Run the chatbot
        conn.close()  # Close connection
    else:
        print("Error: Unable to create database connection.")

if __name__ == '__main__':
    main()
