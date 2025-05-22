import sys
import os
import unittest
import sqlite3
from datetime import datetime, timedelta

# Add the parent directory of 'BackEnd' to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))


from database import (
    Database, UserManager, AddressManager, CategoryManager, ProductManager,
    ReviewManager, CartItemManager, OrderManager, OrderItemManager,
    PaymentManager, DiscountManager, DiscountUsageManager,
    ProductDiscountManager, CategoryDiscountManager
)

class TestDatabase(unittest.TestCase):
    def setUp(self):
        """Set up the database connection and initialize schema."""
        # Initialize Database to ensure schema exists
        self.db = Database()
        self.db.init_db()

        # Establish connection to shop.db
        self.conn = sqlite3.connect('database/shop.db', timeout=10)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.cursor = self.conn.cursor()

        # Clear all tables to ensure a clean state
        tables = [
            'discount_usage', 'product_discounts', 'category_discounts', 'payments',
            'order_items', 'orders', 'cart_items', 'reviews', 'products', 'categories',
            'addresses', 'users'
        ]
        for table in tables:
            self.cursor.execute(f'DELETE FROM {table}')
        self.conn.commit()

        # Initialize managers
        self.user_mgr = UserManager()
        self.address_mgr = AddressManager()
        self.category_mgr = CategoryManager()
        self.product_mgr = ProductManager()
        self.review_mgr = ReviewManager()
        self.cart_mgr = CartItemManager()
        self.order_mgr = OrderManager()
        self.order_item_mgr = OrderItemManager()
        self.payment_mgr = PaymentManager()
        self.discount_mgr = DiscountManager()
        self.discount_usage_mgr = DiscountUsageManager()
        self.product_discount_mgr = ProductDiscountManager()
        self.category_discount_mgr = CategoryDiscountManager()

    def tearDown(self):
        """Close the database connection."""
        self.conn.close()

    def test_user_manager(self):
        """Test UserManager operations."""
        # Test add_user
        user_id = self.user_mgr.add_user("testuser", "test@example.com", "password", "Test User", "+1234567890", 1)
        self.assertIsNotNone(user_id)
        self.assertEqual(self.cursor.execute("SELECT COUNT(*) FROM users").fetchone()[0], 1)

        # Test get_user_by_id
        user = self.user_mgr.get_user_by_id(user_id)
        self.assertEqual(user['username'], "testuser")
        self.assertEqual(user['is_admin'], 1)

        # Test get_user_by_email
        user = self.user_mgr.get_user_by_email("test@example.com")
        self.assertEqual(user['username'], "testuser")

        # Test update_user
        self.assertTrue(self.user_mgr.update_user(user_id, full_name="Updated User", is_admin=0))
        user = self.user_mgr.get_user_by_id(user_id)
        self.assertEqual(user['full_name'], "Updated User")
        self.assertEqual(user['is_admin'], 0)

        # Test validate_password
        self.assertTrue(self.user_mgr.validate_password(user_id, "password"))
        self.assertFalse(self.user_mgr.validate_password(user_id, "wrongpassword"))

        # Test get_users
        users, total = self.user_mgr.get_users(page=1, per_page=10)
        self.assertEqual(len(users), 1)
        self.assertEqual(total, 1)

        # Test delete_user
        self.assertTrue(self.user_mgr.delete_user(user_id))
        self.assertEqual(self.cursor.execute("SELECT COUNT(*) FROM users").fetchone()[0], 0)

    def test_address_manager(self):
        """Test AddressManager operations."""
        user_id = self.user_mgr.add_user("testuser", "test@example.com", "password")
        address_id = self.address_mgr.add_address(user_id, "123 Main St", "New York", "USA", postal_code="10001", is_default=1)
        self.assertIsNotNone(address_id)

        address = self.address_mgr.get_address_by_id(address_id)
        self.assertEqual(address['city'], "New York")
        self.assertEqual(address['is_default'], 1)

        addresses = self.address_mgr.get_addresses_by_user(user_id)
        self.assertEqual(len(addresses), 1)

        self.assertTrue(self.address_mgr.update_address(address_id, city="Boston"))
        address = self.address_mgr.get_address_by_id(address_id)
        self.assertEqual(address['city'], "Boston")

        addresses, total = self.address_mgr.get_addresses(page=1, per_page=10)
        self.assertEqual(len(addresses), 1)
        self.assertEqual(total, 1)

        self.assertTrue(self.address_mgr.delete_address(address_id))
        self.assertEqual(self.cursor.execute("SELECT COUNT(*) FROM addresses").fetchone()[0], 0)

    def test_category_manager(self):
        """Test CategoryManager operations."""
        category_id = self.category_mgr.add_category("Electronics")
        self.assertIsNotNone(category_id)

        category = self.category_mgr.get_category_by_id(category_id)
        self.assertEqual(category['name'], "Electronics")

        sub_category_id = self.category_mgr.add_category("Laptops", parent_id=category_id)
        categories = self.category_mgr.get_categories_by_parent(category_id)
        self.assertEqual(len(categories), 1)
        self.assertEqual(categories[0]['name'], "Laptops")

        self.assertTrue(self.category_mgr.update_category(category_id, name="Gadgets"))
        category = self.category_mgr.get_category_by_id(category_id)
        self.assertEqual(category['name'], "Gadgets")

        categories, total = self.category_mgr.get_categories(page=1, per_page=10)
        self.assertEqual(len(categories), 2)
        self.assertEqual(total, 2)

        self.assertTrue(self.category_mgr.delete_category(sub_category_id))
        self.assertEqual(self.cursor.execute("SELECT COUNT(*) FROM categories").fetchone()[0], 1)

    def test_product_manager(self):
        """Test ProductManager operations."""
        category_id = self.category_mgr.add_category("Electronics")
        product_id = self.product_mgr.add_product("Laptop", 999.99, 50, category_id, "High-performance laptop")
        self.assertIsNotNone(product_id)

        product = self.product_mgr.get_product_by_id(product_id)
        self.assertEqual(product['name'], "Laptop")
        self.assertEqual(product['price'], 999.99)

        products = self.product_mgr.get_products_by_category(category_id)
        self.assertEqual(len(products), 1)

        self.assertTrue(self.product_mgr.update_product(product_id, price=1099.99, stock_quantity=40))
        product = self.product_mgr.get_product_by_id(product_id)
        self.assertEqual(product['price'], 1099.99)

        products, total = self.product_mgr.get_products(page=1, per_page=10)
        self.assertEqual(len(products), 1)
        self.assertEqual(total, 1)

        self.assertTrue(self.product_mgr.delete_product(product_id))
        self.assertEqual(self.cursor.execute("SELECT COUNT(*) FROM products").fetchone()[0], 0)

    def test_review_manager(self):
        """Test ReviewManager operations."""
        user_id = self.user_mgr.add_user("testuser", "test@example.com", "password")
        category_id = self.category_mgr.add_category("Electronics")
        product_id = self.product_mgr.add_product("Laptop", 999.99, 50, category_id)
        review_id = self.review_mgr.add_review(user_id, product_id, 5, "Great product!")
        self.assertIsNotNone(review_id)

        review = self.review_mgr.get_review_by_id(review_id)
        self.assertEqual(review['rating'], 5)
        self.assertEqual(review['comment'], "Great product!")

        reviews = self.review_mgr.get_reviews_by_product(product_id)
        self.assertEqual(len(reviews), 1)

        self.assertTrue(self.review_mgr.update_review(review_id, rating=4, comment="Very good!"))
        review = self.review_mgr.get_review_by_id(review_id)
        self.assertEqual(review['rating'], 4)

        reviews, total = self.review_mgr.get_reviews(page=1, per_page=10)
        self.assertEqual(len(reviews), 1)
        self.assertEqual(total, 1)

        self.assertTrue(self.review_mgr.delete_review(review_id))
        self.assertEqual(self.cursor.execute("SELECT COUNT(*) FROM reviews").fetchone()[0], 0)

    def test_cart_item_manager(self):
        """Test CartItemManager operations."""
        user_id = self.user_mgr.add_user("testuser", "test@example.com", "password")
        category_id = self.category_mgr.add_category("Electronics")
        product_id = self.product_mgr.add_product("Laptop", 999.99, 50, category_id)
        cart_item_id = self.cart_mgr.add_cart_item(user_id, product_id, 2)
        self.assertIsNotNone(cart_item_id)

        cart_item = self.cart_mgr.get_cart_item_by_id(cart_item_id)
        self.assertEqual(cart_item['quantity'], 2)
        self.assertEqual(cart_item['product_id'], product_id)

        cart_items = self.cart_mgr.get_cart_items_by_user(user_id)
        self.assertEqual(len(cart_items), 1)
        self.assertEqual(cart_items[0]['name'], "Laptop")

        self.assertTrue(self.cart_mgr.update_cart_item(cart_item_id, quantity=3))
        cart_item = self.cart_mgr.get_cart_item_by_id(cart_item_id)
        self.assertEqual(cart_item['quantity'], 3)

        cart_items, total = self.cart_mgr.get_cart_items(page=1, per_page=10)
        self.assertEqual(len(cart_items), 1)
        self.assertEqual(total, 1)

        self.assertTrue(self.cart_mgr.delete_cart_item(cart_item_id))
        self.assertEqual(self.cursor.execute("SELECT COUNT(*) FROM cart_items").fetchone()[0], 0)

    def test_order_manager(self):
        """Test OrderManager operations."""
        user_id = self.user_mgr.add_user("testuser", "test@example.com", "password")
        address_id = self.address_mgr.add_address(user_id, "123 Main St", "New York", "USA")
        order_id = self.order_mgr.add_order(user_id, address_id, 999.99)
        self.assertIsNotNone(order_id)

        order = self.order_mgr.get_order_by_id(order_id)
        self.assertEqual(order['total_price'], 999.99)
        self.assertEqual(order['status'], "pending")

        orders = self.order_mgr.get_orders_by_user(user_id)
        self.assertEqual(len(orders), 1)

        self.assertTrue(self.order_mgr.update_order(order_id, status="shipped", total_price=1099.99))
        order = self.order_mgr.get_order_by_id(order_id)
        self.assertEqual(order['status'], "shipped")
        self.assertEqual(order['total_price'], 1099.99)

        orders, total = self.order_mgr.get_orders(page=1, per_page=10)
        self.assertEqual(len(orders), 1)
        self.assertEqual(total, 1)

        self.assertTrue(self.order_mgr.delete_order(order_id))
        self.assertEqual(self.cursor.execute("SELECT COUNT(*) FROM orders").fetchone()[0], 0)

    def test_order_item_manager(self):
        """Test OrderItemManager operations."""
        user_id = self.user_mgr.add_user("testuser", "test@example.com", "password")
        address_id = self.address_mgr.add_address(user_id, "123 Main St", "New York", "USA")
        order_id = self.order_mgr.add_order(user_id, address_id, 999.99)
        category_id = self.category_mgr.add_category("Electronics")
        product_id = self.product_mgr.add_product("Laptop", 999.99, 50, category_id)
        order_item_id = self.order_item_mgr.add_order_item(order_id, product_id, 2, 499.99)
        self.assertIsNotNone(order_item_id)

        order_item = self.order_item_mgr.get_order_item_by_id(order_item_id)
        self.assertEqual(order_item['quantity'], 2)
        self.assertEqual(order_item['price'], 499.99)

        order_items = self.order_item_mgr.get_order_items_by_order(order_id)
        self.assertEqual(len(order_items), 1)
        self.assertEqual(order_items[0]['name'], "Laptop")

        self.assertTrue(self.order_item_mgr.update_order_item(order_item_id, quantity=3, price=599.99))
        order_item = self.order_item_mgr.get_order_item_by_id(order_item_id)
        self.assertEqual(order_item['quantity'], 3)
        self.assertEqual(order_item['price'], 599.99)

        order_items, total = self.order_item_mgr.get_order_items(page=1, per_page=10)
        self.assertEqual(len(order_items), 1)
        self.assertEqual(total, 1)

        self.assertTrue(self.order_item_mgr.delete_order_item(order_item_id))
        self.assertEqual(self.cursor.execute("SELECT COUNT(*) FROM order_items").fetchone()[0], 0)

    def test_payment_manager(self):
        """Test PaymentManager operations."""
        user_id = self.user_mgr.add_user("testuser", "test@example.com", "password")
        address_id = self.address_mgr.add_address(user_id, "123 Main St", "New York", "USA")
        order_id = self.order_mgr.add_order(user_id, address_id, 999.99)
        payment_id = self.payment_mgr.add_payment(order_id, "credit_card", "TX123", "paid")
        self.assertIsNotNone(payment_id)

        payment = self.payment_mgr.get_payment_by_id(payment_id)
        self.assertEqual(payment['payment_method'], "credit_card")
        self.assertEqual(payment['payment_status'], "paid")
        self.assertIsNotNone(payment['paid_at'])

        payments = self.payment_mgr.get_payments_by_order(order_id)
        self.assertEqual(len(payments), 1)

        self.assertTrue(self.payment_mgr.update_payment(payment_id, payment_status="failed"))
        payment = self.payment_mgr.get_payment_by_id(payment_id)
        self.assertEqual(payment['payment_status'], "failed")
        self.assertIsNone(payment['paid_at'])

        payments, total = self.payment_mgr.get_payments(page=1, per_page=10)
        self.assertEqual(len(payments), 1)
        self.assertEqual(total, 1)

        self.assertTrue(self.payment_mgr.delete_payment(payment_id))
        self.assertEqual(self.cursor.execute("SELECT COUNT(*) FROM payments").fetchone()[0], 0)

    def test_discount_manager(self):
        """Test DiscountManager operations."""
        expires_at = (datetime.utcnow() + timedelta(days=30)).isoformat() + "Z"
        discount_id = self.discount_mgr.add_discount("SAVE10", 10.0, 100, expires_at, "10% off")
        self.assertIsNotNone(discount_id)

        discount = self.discount_mgr.get_discount_by_id(discount_id)
        self.assertEqual(discount['code'], "SAVE10")
        self.assertEqual(discount['discount_percent'], 10.0)

        discount = self.discount_mgr.get_discount_by_code("SAVE10")
        self.assertEqual(discount['code'], "SAVE10")

        valid_discount = self.discount_mgr.get_valid_discount("SAVE10")
        self.assertEqual(valid_discount['code'], "SAVE10")

        self.assertTrue(self.discount_mgr.update_discount(discount_id, discount_percent=15.0, is_active=0))
        discount = self.discount_mgr.get_discount_by_id(discount_id)
        self.assertEqual(discount['discount_percent'], 15.0)
        self.assertEqual(discount['is_active'], 0)

        discounts, total = self.discount_mgr.get_discounts(page=1, per_page=10)
        self.assertEqual(len(discounts), 1)
        self.assertEqual(total, 1)

        self.assertTrue(self.discount_mgr.delete_discount(discount_id))
        self.assertEqual(self.cursor.execute("SELECT COUNT(*) FROM discounts").fetchone()[0], 0)

    def test_discount_usage_manager(self):
        """Test DiscountUsageManager operations."""
        user_id = self.user_mgr.add_user("testuser", "test@example.com", "password")
        discount_id = self.discount_mgr.add_discount("SAVE10", 10.0, 100)
        usage_id = self.discount_usage_mgr.add_discount_usage(discount_id, user_id)
        self.assertIsNotNone(usage_id)

        usage = self.discount_usage_mgr.get_discount_usage_by_id(usage_id)
        self.assertEqual(usage['discount_id'], discount_id)
        self.assertEqual(usage['user_id'], user_id)

        usages = self.discount_usage_mgr.get_discount_usages_by_discount(discount_id)
        self.assertEqual(len(usages), 1)

        usages = self.discount_usage_mgr.get_discount_usages_by_user(user_id)
        self.assertEqual(len(usages), 1)

        usages, total = self.discount_usage_mgr.get_discount_usages(page=1, per_page=10)
        self.assertEqual(len(usages), 1)
        self.assertEqual(total, 1)
        self.assertEqual(usages[0]['code'], "SAVE10")

        self.assertTrue(self.discount_usage_mgr.delete_discount_usage(usage_id))
        self.assertEqual(self.cursor.execute("SELECT COUNT(*) FROM discount_usage").fetchone()[0], 0)

    def test_product_discount_manager(self):
        """Test ProductDiscountManager operations."""
        category_id = self.category_mgr.add_category("Electronics")
        product_id = self.product_mgr.add_product("Laptop", 999.99, 50, category_id)
        starts_at = datetime.utcnow().isoformat() + "Z"
        ends_at = (datetime.utcnow() + timedelta(days=30)).isoformat() + "Z"
        discount_id = self.product_discount_mgr.add_product_discount(product_id, 15.0, starts_at, ends_at)
        self.assertIsNotNone(discount_id)

        discount = self.product_discount_mgr.get_product_discount_by_id(discount_id)
        self.assertEqual(discount['product_id'], product_id)
        self.assertEqual(discount['discount_percent'], 15.0)

        discounts = self.product_discount_mgr.get_product_discounts_by_product(product_id)
        self.assertEqual(len(discounts), 1)

        valid_discounts = self.product_discount_mgr.get_valid_product_discounts(product_id)
        self.assertEqual(len(valid_discounts), 1)

        self.assertTrue(self.product_discount_mgr.update_product_discount(discount_id, discount_percent=20.0, is_active=0))
        discount = self.product_discount_mgr.get_product_discount_by_id(discount_id)
        self.assertEqual(discount['discount_percent'], 20.0)
        self.assertEqual(discount['is_active'], 0)

        discounts, total = self.product_discount_mgr.get_product_discounts(page=1, per_page=10)
        self.assertEqual(len(discounts), 1)
        self.assertEqual(total, 1)
        self.assertEqual(discounts[0]['name'], "Laptop")

        self.assertTrue(self.product_discount_mgr.delete_product_discount(discount_id))
        self.assertEqual(self.cursor.execute("SELECT COUNT(*) FROM product_discounts").fetchone()[0], 0)

    def test_category_discount_manager(self):
        """Test CategoryDiscountManager operations."""
        category_id = self.category_mgr.add_category("Electronics")
        starts_at = datetime.utcnow().isoformat() + "Z"
        ends_at = (datetime.utcnow() + timedelta(days=30)).isoformat() + "Z"
        discount_id = self.category_discount_mgr.add_category_discount(category_id, 10.0, starts_at, ends_at)
        self.assertIsNotNone(discount_id)

        discount = self.category_discount_mgr.get_category_discount_by_id(discount_id)
        self.assertEqual(discount['category_id'], category_id)
        self.assertEqual(discount['discount_percent'], 10.0)

        discounts = self.category_discount_mgr.get_category_discounts_by_category(category_id)
        self.assertEqual(len(discounts), 1)

        valid_discounts = self.category_discount_mgr.get_valid_category_discounts(category_id)
        self.assertEqual(len(valid_discounts), 1)

        self.assertTrue(self.category_discount_mgr.update_category_discount(discount_id, discount_percent=15.0, is_active=0))
        discount = self.category_discount_mgr.get_category_discount_by_id(discount_id)
        self.assertEqual(discount['discount_percent'], 15.0)
        self.assertEqual(discount['is_active'], 0)

        discounts, total = self.category_discount_mgr.get_category_discounts(page=1, per_page=10)
        self.assertEqual(len(discounts), 1)
        self.assertEqual(total, 1)
        self.assertEqual(discounts[0]['name'], "Electronics")

        self.assertTrue(self.category_discount_mgr.delete_category_discount(discount_id))
        self.assertEqual(self.cursor.execute("SELECT COUNT(*) FROM category_discounts").fetchone()[0], 0)

if __name__ == '__main__':
    unittest.main()