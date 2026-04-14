import sqlite3

# Connect to database
conn = sqlite3.connect("kow.db")
cursor = conn.cursor()

def create_tables():
    """Initialize database tables"""
    
    # Create users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            name VARCHAR(100),
            email VARCHAR(100)
        )
    """)
    
    # Create products table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            product_id INTEGER PRIMARY KEY,
            name VARCHAR(100),
            stock INTEGER,
            price REAL
        )
    """)
    
    # Create orders table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            product_id INTEGER,
            amount REAL,
            status VARCHAR(50),
            FOREIGN KEY(user_id) REFERENCES users(user_id),
            FOREIGN KEY(product_id) REFERENCES products(product_id)
        )
    """)
    
    # Create payments table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER,
            payment_status VARCHAR(50),
            FOREIGN KEY(order_id) REFERENCES orders(order_id)
        )
    """)
    
    conn.commit()
    print("Database tables created successfully")

# Initialize tables
create_tables()

def insert_sample_data():
    """Insert sample data for testing"""
    try:
        # Insert sample users
        cursor.execute("INSERT OR IGNORE INTO users (user_id, name, email) VALUES (1, 'Alice', 'alice@example.com')")
        cursor.execute("INSERT OR IGNORE INTO users (user_id, name, email) VALUES (2, 'Bob', 'bob@example.com')")
        cursor.execute("INSERT OR IGNORE INTO users (user_id, name, email) VALUES (3, 'Charlie', 'charlie@example.com')")
        
        # Insert sample products
        cursor.execute("INSERT OR IGNORE INTO products (product_id, name, stock, price) VALUES (101, 'Laptop', 5, 999.99)")
        cursor.execute("INSERT OR IGNORE INTO products (product_id, name, stock, price) VALUES (102, 'Phone', 0, 699.99)")
        
        conn.commit()
        print("Sample data inserted successfully\n")
    except Exception as e:
        print(f"Error inserting sample data: {e}")

def process_payment(user_id, product_id):
    try:
        print(f"\nUser ID: {user_id}")
        print(f"Product ID: {product_id}\n")
        
        conn.execute("BEGIN TRANSACTION")

        # Check stock
        print("Checking stock...")
        cursor.execute("SELECT stock, price FROM products WHERE product_id = ?", (product_id,))
        product = cursor.fetchone()

        if product is None:
            print("Product not found")
            print("Transaction Aborted")
            conn.rollback()
            return

        stock, price = product

        if stock <= 0:
            print("Out of stock")
            print("Transaction Aborted")
            conn.rollback()
            return

        print("Stock available")
        print("Processing payment...")
        
        # Reduce stock
        print("Reducing inventory...")
        cursor.execute("UPDATE products SET stock = stock - 1 WHERE product_id = ?", (product_id,))

        # Create order
        print("Creating order record...")
        cursor.execute("INSERT INTO orders (user_id, product_id, amount, status) VALUES (?, ?, ?, ?)",
                       (user_id, product_id, price, "CONFIRMED"))

        order_id = cursor.lastrowid

        # Add payment record
        print("Recording payment...")
        cursor.execute("INSERT INTO payments (order_id, payment_status) VALUES (?, ?)",
                       (order_id, "SUCCESS"))

        conn.commit()
        print(f"\nPayment Successful. Order ID: {order_id}")

    except Exception as e:
        conn.rollback()
        print("Error occurred")
        print("Transaction Failed")
        print("Rollback executed")

# Insert sample data
insert_sample_data()

# Test cases
print("="*50)
print("Case 1: Successful Payment")
print("="*50)
process_payment(1, 101)

print("\n" + "="*50)
print("Case 2: Out of Stock")
print("="*50)
process_payment(2, 101)

print("\n" + "="*50)
print("Case 3: Simulated Failure")
print("="*50)
process_payment(3, 101)