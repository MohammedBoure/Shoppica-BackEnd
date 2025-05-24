import sqlite3
import logging
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DatabaseTest:
    DB_FILE = 'database/shop.db' # تأكد أن هذا المسار صحيح

    def __init__(self):
        if not os.path.exists(self.DB_FILE):
            logging.error(f"Database file not found at {self.DB_FILE}. Please run the main script to create it first.")
            raise FileNotFoundError(f"Database file not found at {self.DB_FILE}")

    def get_db_connection(self):
        """Establishes a new SQLite connection with row factory and foreign key support."""
        try:
            conn = sqlite3.connect(self.DB_FILE, timeout=10)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON") # Good practice, though not strictly needed for SELECT
            return conn
        except sqlite3.Error as e:
            logging.error(f"Database connection error: {e}")
            raise

    def display_table_data(self, table_name):
        """Fetches and displays all data from a specified table."""
        print(f"\n--- Data from table: {table_name} ---")
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(f"SELECT * FROM {table_name}")
                rows = cursor.fetchall()

                if not rows:
                    print(f"No data found in {table_name}.")
                    return

                # Print column headers
                column_names = [description[0] for description in cursor.description]
                print(" | ".join(column_names))
                print("-" * (len(" | ".join(column_names)) + len(column_names)*2)) # Dynamic separator

                # Print rows
                for row in rows:
                    print(" | ".join(str(value) for value in row))
            print(f"--- End of data for {table_name} ---")
        except sqlite3.Error as e:
            logging.error(f"Error fetching data from {table_name}: {e}")
            print(f"Could not retrieve data from {table_name}.")

    def display_all_tables_data(self):
        """Displays data from all known tables in the database."""
        # قائمة الجداول كما هي معرفة في كود قاعدة البيانات الأصلي
        table_names = [
            'users',
            'addresses',
            'categories',
            'products',
            'reviews',
            'cart_items',
            'orders',
            'order_items',
            'payments',
            'discounts',
            'discount_usage',
            'product_discounts',
            'category_discounts'
        ]

        logging.info("Attempting to display data from all tables...")
        for table_name in table_names:
            self.display_table_data(table_name)
        logging.info("Finished displaying table data.")

# --- الكود الرئيسي لتشغيل الاختبار ---
if __name__ == '__main__':
    # أولاً، قم بإنشاء قاعدة البيانات والجداول إذا لم تكن موجودة
    # (هذا الجزء للتأكد فقط، يمكنك إزالته إذا كنت متأكدًا أن قاعدة البيانات موجودة)
    # --- بداية: تأكد من وجود قاعدة البيانات (يمكن إزالة هذا الجزء إذا تم إنشاء القاعدة مسبقًا) ---
    class MainDatabase: # نسخة مبسطة من كلاس قاعدة البيانات الأصلي فقط لإنشاء الملف
        DB_FILE = 'database/shop.db'

        @staticmethod
        def hash_password(password):
            from passlib.hash import scrypt
            return scrypt.hash(password)

        @staticmethod
        def get_current_timestamp():
            from datetime import datetime, timezone
            return datetime.now(timezone.utc).isoformat()

        def __init__(self):
            db_dir = os.path.dirname(self.DB_FILE)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir)
                logging.info(f"Created directory: {db_dir}")
            self.init_db_if_not_exists()


        def get_db_connection(self):
            conn = sqlite3.connect(self.DB_FILE, timeout=10)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON")
            return conn

        def init_db_if_not_exists(self):
            if os.path.exists(self.DB_FILE):
                logging.info(f"Database file {self.DB_FILE} already exists. Skipping schema creation in test setup.")
                # يمكنك إضافة هنا تحقق من وجود الجداول إذا أردت
                return

            # نفس كود init_db من الكلاس الأصلي
            try:
                with self.get_db_connection() as conn:
                    cursor = conn.cursor()
                    logging.info("Initializing database schema for testing...")
                    cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL UNIQUE, email TEXT NOT NULL UNIQUE, password_hash TEXT NOT NULL, full_name TEXT, phone_number TEXT, is_admin INTEGER DEFAULT 0 CHECK(is_admin IN (0, 1)), created_at TEXT DEFAULT (datetime('now', 'utc')))")
                    cursor.execute("SELECT id FROM users WHERE email = ?", ('admin@gmail.com',))
                    if not cursor.fetchone():
                        admin_password_hash = self.hash_password('admin')
                        cursor.execute("INSERT INTO users (username, email, password_hash, is_admin, created_at) VALUES (?, ?, ?, ?, ?)", ('admin', 'admin@gmail.com', admin_password_hash, 1, self.get_current_timestamp()))
                    cursor.execute("CREATE TABLE IF NOT EXISTS addresses (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, address_line1 TEXT, address_line2 TEXT, city TEXT, state TEXT, postal_code TEXT, country TEXT, is_default INTEGER DEFAULT 0 CHECK(is_default IN (0, 1)), FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE)")
                    cursor.execute("CREATE TABLE IF NOT EXISTS categories (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, parent_id INTEGER, FOREIGN KEY (parent_id) REFERENCES categories(id) ON DELETE SET NULL)")
                    cursor.execute("CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, description TEXT, price REAL NOT NULL, stock_quantity INTEGER NOT NULL, category_id INTEGER, image_url TEXT, is_active INTEGER DEFAULT 1 CHECK(is_active IN (0, 1)), created_at TEXT DEFAULT (datetime('now', 'utc')), FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL)")
                    cursor.execute("CREATE TABLE IF NOT EXISTS reviews (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, product_id INTEGER NOT NULL, rating INTEGER CHECK (rating BETWEEN 1 AND 5), comment TEXT, created_at TEXT DEFAULT (datetime('now', 'utc')), FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE, FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE)")
                    cursor.execute("CREATE TABLE IF NOT EXISTS cart_items (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, product_id INTEGER NOT NULL, quantity INTEGER NOT NULL, added_at TEXT DEFAULT (datetime('now', 'utc')), FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE, FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE)")
                    cursor.execute("CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'shipped', 'delivered', 'canceled')), total_price REAL, shipping_address_id INTEGER, created_at TEXT DEFAULT (datetime('now', 'utc')), FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE, FOREIGN KEY (shipping_address_id) REFERENCES addresses(id) ON DELETE SET NULL)")
                    cursor.execute("CREATE TABLE IF NOT EXISTS order_items (id INTEGER PRIMARY KEY AUTOINCREMENT, order_id INTEGER NOT NULL, product_id INTEGER NOT NULL, quantity INTEGER NOT NULL, price REAL NOT NULL, FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE, FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE)")
                    cursor.execute("CREATE TABLE IF NOT EXISTS payments (id INTEGER PRIMARY KEY AUTOINCREMENT, order_id INTEGER NOT NULL, payment_method TEXT, payment_status TEXT DEFAULT 'unpaid' CHECK(payment_status IN ('paid', 'unpaid', 'failed')), transaction_id TEXT, paid_at TEXT, FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE)")
                    cursor.execute("CREATE TABLE IF NOT EXISTS discounts (id INTEGER PRIMARY KEY AUTOINCREMENT, code TEXT NOT NULL UNIQUE, description TEXT, discount_percent REAL, max_uses INTEGER, expires_at TEXT, is_active INTEGER DEFAULT 1 CHECK(is_active IN (0, 1)))")
                    cursor.execute("CREATE TABLE IF NOT EXISTS discount_usage (id INTEGER PRIMARY KEY AUTOINCREMENT, discount_id INTEGER NOT NULL, user_id INTEGER NOT NULL, used_at TEXT DEFAULT (datetime('now', 'utc')), FOREIGN KEY (discount_id) REFERENCES discounts(id) ON DELETE CASCADE, FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE)")
                    cursor.execute("CREATE TABLE IF NOT EXISTS product_discounts (id INTEGER PRIMARY KEY AUTOINCREMENT, product_id INTEGER NOT NULL, discount_percent REAL NOT NULL, starts_at TEXT, ends_at TEXT, is_active INTEGER DEFAULT 1 CHECK(is_active IN (0, 1)), FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE)")
                    cursor.execute("CREATE TABLE IF NOT EXISTS category_discounts (id INTEGER PRIMARY KEY AUTOINCREMENT, category_id INTEGER NOT NULL, discount_percent REAL NOT NULL, starts_at TEXT, ends_at TEXT, is_active INTEGER DEFAULT 1 CHECK(is_active IN (0, 1)), FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE)")
                    conn.commit()
                    logging.info("Database schema initialization complete for testing.")
            except sqlite3.Error as e:
                logging.error(f"Database initialization failed during test setup: {e}")
                raise
    # --- نهاية: تأكد من وجود قاعدة البيانات ---

    # قم بإنشاء كائن Database للتأكد من أن قاعدة البيانات والجداول موجودة
    # إذا لم تقم بتضمين الكود أعلاه، تأكد من تشغيل السكريبت الأصلي أولاً
    try:
        print("Ensuring database and tables exist (running a minimal init)...")
        # هذا السطر سينشئ المجلد database والملف shop.db إذا لم يكونا موجودين
        # ويضيف المستخدم admin الافتراضي إذا لم يكن موجودًا
        db_initializer = MainDatabase() # استخدم الكلاس المبسط لإنشاء قاعدة البيانات فقط عند الحاجة
        print("Database check/initialization complete.")

        # الآن قم بتشغيل اختبار عرض البيانات
        print("\nStarting data display test...")
        db_tester = DatabaseTest()
        db_tester.display_all_tables_data()
        print("\nData display test finished.")

    except FileNotFoundError:
        print(f"Test cannot run because the database file was not found and could not be created.")
    except Exception as e:
        logging.error(f"An error occurred during the test: {e}")
        print(f"An error occurred: {e}")