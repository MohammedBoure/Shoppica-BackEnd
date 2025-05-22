import sqlite3
import logging
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Database:
    """Base class for managing SQLite database connections and schema initialization."""
    
    DB_FILE = 'database/shop.db'

    def __init__(self):
        """Initialize the database and create schema."""
        self.init_db()

    def get_db_connection(self):
        """Establishes a new SQLite connection with row factory and foreign key support."""
        try:
            conn = sqlite3.connect(self.DB_FILE, timeout=10)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON")
            return conn
        except sqlite3.Error as e:
            logging.error(f"Database connection error: {e}")
            raise

    def init_db(self):
        """Initializes the database schema with tables and indexes."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                logging.info("Initializing database schema...")

                # Create users table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL UNIQUE,
                        email TEXT NOT NULL UNIQUE,
                        password_hash TEXT NOT NULL,
                        full_name TEXT,
                        phone_number TEXT,
                        is_admin INTEGER DEFAULT 0 CHECK(is_admin IN (0, 1)),
                        created_at TEXT DEFAULT (datetime('now'))
                    )
                ''')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)')
                logging.info("Table 'users' checked/created.")

                # Create addresses table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS addresses (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        address_line1 TEXT,
                        address_line2 TEXT,
                        city TEXT,
                        state TEXT,
                        postal_code TEXT,
                        country TEXT,
                        is_default INTEGER DEFAULT 0 CHECK(is_default IN (0, 1)),
                        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                    )
                ''')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_addresses_user_id ON addresses(user_id)')
                logging.info("Table 'addresses' checked/created.")

                # Create categories table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS categories (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        parent_id INTEGER,
                        FOREIGN KEY (parent_id) REFERENCES categories(id) ON DELETE SET NULL
                    )
                ''')
                logging.info("Table 'categories' checked/created.")

                # Create products table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS products (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        description TEXT,
                        price REAL NOT NULL,
                        stock_quantity INTEGER NOT NULL,
                        category_id INTEGER,
                        image_url TEXT,
                        is_active INTEGER DEFAULT 1 CHECK(is_active IN (0, 1)),
                        created_at TEXT DEFAULT (datetime('now')),
                        FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
                    )
                ''')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_products_category_id ON products(category_id)')
                logging.info("Table 'products' checked/created.")

                # Create reviews table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS reviews (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        product_id INTEGER NOT NULL,
                        rating INTEGER CHECK (rating BETWEEN 1 AND 5),
                        comment TEXT,
                        created_at TEXT DEFAULT (datetime('now')),
                        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                        FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
                    )
                ''')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_reviews_product_id ON reviews(product_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_reviews_user_id ON reviews(user_id)')
                logging.info("Table 'reviews' checked/created.")

                # Create cart_items table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS cart_items (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        product_id INTEGER NOT NULL,
                        quantity INTEGER NOT NULL,
                        added_at TEXT DEFAULT (datetime('now')),
                        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                        FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
                    )
                ''')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_cart_items_user_id ON cart_items(user_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_cart_items_product_id ON cart_items(product_id)')
                logging.info("Table 'cart_items' checked/created.")

                # Create orders table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS orders (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'shipped', 'delivered', 'canceled')),
                        total_price REAL,
                        shipping_address_id INTEGER,
                        created_at TEXT DEFAULT (datetime('now')),
                        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                        FOREIGN KEY (shipping_address_id) REFERENCES addresses(id) ON DELETE SET NULL
                    )
                ''')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id)')
                logging.info("Table 'orders' checked/created.")

                # Create order_items table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS order_items (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        order_id INTEGER NOT NULL,
                        product_id INTEGER NOT NULL,
                        quantity INTEGER NOT NULL,
                        price REAL NOT NULL,
                        FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
                        FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
                    )
                ''')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON order_items(order_id)')
                logging.info("Table 'order_items' checked/created.")

                # Create payments table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS payments (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        order_id INTEGER NOT NULL,
                        payment_method TEXT,
                        payment_status TEXT DEFAULT 'unpaid' CHECK(payment_status IN ('paid', 'unpaid', 'failed')),
                        transaction_id TEXT,
                        paid_at TEXT,
                        FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE
                    )
                ''')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_payments_order_id ON payments(order_id)')
                logging.info("Table 'payments' checked/created.")

                # Create discounts table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS discounts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        code TEXT NOT NULL UNIQUE,
                        description TEXT,
                        discount_percent REAL,
                        max_uses INTEGER,
                        expires_at TEXT,
                        is_active INTEGER DEFAULT 1 CHECK(is_active IN (0, 1))
                    )
                ''')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_discounts_code ON discounts(code)')
                logging.info("Table 'discounts' checked/created.")

                # Create discount_usage table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS discount_usage (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        discount_id INTEGER NOT NULL,
                        user_id INTEGER NOT NULL,
                        used_at TEXT DEFAULT (datetime('now')),
                        FOREIGN KEY (discount_id) REFERENCES discounts(id) ON DELETE CASCADE,
                        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                    )
                ''')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_discount_usage_discount_id ON discount_usage(discount_id)')
                logging.info("Table 'discount_usage' checked/created.")

                # Create product_discounts table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS product_discounts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        product_id INTEGER NOT NULL,
                        discount_percent REAL NOT NULL,
                        starts_at TEXT,
                        ends_at TEXT,
                        is_active INTEGER DEFAULT 1 CHECK(is_active IN (0, 1)),
                        FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
                    )
                ''')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_product_discounts_product_id ON product_discounts(product_id)')
                logging.info("Table 'product_discounts' checked/created.")

                # Create category_discounts table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS category_discounts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        category_id INTEGER NOT NULL,
                        discount_percent REAL NOT NULL,
                        starts_at TEXT,
                        ends_at TEXT,
                        is_active INTEGER DEFAULT 1 CHECK(is_active IN (0, 1)),
                        FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
                    )
                ''')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_category_discounts_category_id ON category_discounts(category_id)')
                logging.info("Table 'category_discounts' checked/created.")

                conn.commit()
                logging.info("Database schema initialization complete.")
        except sqlite3.Error as e:
            logging.error(f"Database initialization failed: {e}")
            raise

    @staticmethod
    def hash_password(password):
        """Hashes a password using werkzeug.security."""
        return generate_password_hash(password)

    @staticmethod
    def check_password(pwhash, password):
        """Checks if a password matches the stored hash."""
        return check_password_hash(pwhash, password)

    @staticmethod
    def get_current_timestamp():
        """Returns the current UTC timestamp in ISO8601 format."""
        return datetime.utcnow().isoformat() + "Z"