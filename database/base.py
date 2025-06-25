import logging
from datetime import datetime
from passlib.hash import scrypt
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Index, text
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.event import listens_for
from sqlalchemy.pool import StaticPool
from sqlalchemy.engine import Engine

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# SQLAlchemy Base
Base = declarative_base()

# Database URL for SQLite
DATABASE_URL = "sqlite:///shop.db"

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=False, unique=True)
    password_hash = Column(String, nullable=False)
    full_name = Column(String)
    phone_number = Column(String)
    is_admin = Column(Integer, default=0, nullable=False)  # SQLite does not enforce CheckConstraint
    created_at = Column(DateTime, default=datetime.utcnow)  # Removed timezone=True for SQLite compatibility
    
    # Relationships
    addresses = relationship("Address", back_populates="user", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="user", cascade="all, delete-orphan")
    cart_items = relationship("CartItem", back_populates="user", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="user", cascade="all, delete-orphan")
    discount_usages = relationship("DiscountUsage", back_populates="user", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_users_username', 'username'),
        Index('idx_users_email', 'email'),
    )

class Address(Base):
    __tablename__ = 'addresses'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)  # SQLite does not enforce ON DELETE
    address_line = Column(String)
    city = Column(String)
    state = Column(String)
    postal_code = Column(String)
    is_default = Column(Integer, default=0, nullable=False)
    
    # Relationship
    user = relationship("User", back_populates="addresses")
    
    __table_args__ = (
        Index('idx_addresses_user_id', 'user_id'),
    )

class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    parent_id = Column(Integer, ForeignKey('categories.id'))
    image_url = Column(String, nullable=False)
    
    # Relationships
    parent = relationship("Category", remote_side=[id])
    products = relationship("Product", back_populates="category")
    discounts = relationship("CategoryDiscount", back_populates="category", cascade="all, delete-orphan")

class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(String)
    price = Column(Float, nullable=False)
    stock_quantity = Column(Integer, nullable=False)
    low_stock_threshold = Column(Integer, default=5, nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'))
    image_url = Column(String)
    is_active = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    category = relationship("Category", back_populates="products")
    images = relationship("ProductImage", back_populates="product", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="product", cascade="all, delete-orphan")
    cart_items = relationship("CartItem", back_populates="product", cascade="all, delete-orphan")
    order_items = relationship("OrderItem", back_populates="product", cascade="all, delete-orphan")
    discounts = relationship("ProductDiscount", back_populates="product", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_products_category_id', 'category_id'),
    )

class ProductImage(Base):
    __tablename__ = 'product_images'
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    image_url = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    product = relationship("Product", back_populates="images")
    
    __table_args__ = (
        Index('idx_product_images_product_id', 'product_id'),
    )

class Review(Base):
    __tablename__ = 'reviews'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    rating = Column(Integer, nullable=False)
    comment = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="reviews")
    product = relationship("Product", back_populates="reviews")
    
    __table_args__ = (
        Index('idx_reviews_product_id', 'product_id'),
        Index('idx_reviews_user_id', 'user_id'),
    )

class CartItem(Base):
    __tablename__ = 'cart_items'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    added_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="cart_items")
    product = relationship("Product", back_populates="cart_items")
    
    __table_args__ = (
        Index('idx_cart_items_user_id', 'user_id'),
        Index('idx_cart_items_product_id', 'product_id'),
    )

class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    status = Column(String, default='pending', nullable=False)
    total_price = Column(Float)
    shipping_address_id = Column(Integer, ForeignKey('addresses.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="orders")
    shipping_address = relationship("Address")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="order", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_orders_user_id', 'user_id'),
    )

class OrderItem(Base):
    __tablename__ = 'order_items'
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    
    # Relationships
    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")
    
    __table_args__ = (
        Index('idx_order_items_order_id', 'order_id'),
    )

class Payment(Base):
    __tablename__ = 'payments'
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    payment_method = Column(String)
    payment_status = Column(String, default='unpaid', nullable=False)
    transaction_id = Column(String)
    paid_at = Column(DateTime)
    
    # Relationship
    order = relationship("Order", back_populates="payments")
    
    __table_args__ = (
        Index('idx_payments_order_id', 'order_id'),
    )

class Discount(Base):
    __tablename__ = 'discounts'
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String, nullable=False, unique=True)
    description = Column(String)
    discount_percent = Column(Float)
    max_uses = Column(Integer)
    expires_at = Column(DateTime)
    is_active = Column(Integer, default=1, nullable=False)
    
    # Relationship
    usages = relationship("DiscountUsage", back_populates="discount", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_discounts_code', 'code'),
    )

class DiscountUsage(Base):
    __tablename__ = 'discount_usage'
    id = Column(Integer, primary_key=True, autoincrement=True)
    discount_id = Column(Integer, ForeignKey('discounts.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    used_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    discount = relationship("Discount", back_populates="usages")
    user = relationship("User", back_populates="discount_usages")
    
    __table_args__ = (
        Index('idx_discount_usage_discount_id', 'discount_id'),
    )

class ProductDiscount(Base):
    __tablename__ = 'product_discounts'
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    discount_percent = Column(Float, nullable=False)
    starts_at = Column(DateTime)
    ends_at = Column(DateTime)
    is_active = Column(Integer, default=1, nullable=False)
    
    # Relationship
    product = relationship("Product", back_populates="discounts")
    
    __table_args__ = (
        Index('idx_product_discounts_product_id', 'product_id'),
    )

class CategoryDiscount(Base):
    __tablename__ = 'category_discounts'
    id = Column(Integer, primary_key=True, autoincrement=True)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False)
    discount_percent = Column(Float, nullable=False)
    starts_at = Column(DateTime)
    ends_at = Column(DateTime)
    is_active = Column(Integer, default=1, nullable=False)
    
    # Relationship
    category = relationship("Category", back_populates="discounts")
    
    __table_args__ = (
        Index('idx_category_discounts_category_id', 'category_id'),
    )

class Database:
    """Base class for managing SQLAlchemy database connections and schema initialization."""
    
    def __init__(self):
        """Initialize the database and create schema."""
        self.engine = create_engine(
            DATABASE_URL,
            connect_args={"check_same_thread": False},  # Required for SQLite in multi-threaded apps
            poolclass=StaticPool  # Optional: Use StaticPool for simplicity in single-threaded apps
        )
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.init_db()

    def get_db_session(self):
        """Returns a new SQLAlchemy session."""
        session = self.SessionLocal()
        try:
            yield session
        finally:
            session.close()

    def init_db(self):
        """Initializes the database schema with tables and indexes."""
        try:
            logging.info("Initializing database schema...")
            Base.metadata.create_all(bind=self.engine)
            
            # Enable foreign key support in SQLite
            with self.engine.connect() as connection:
                connection.execute(text("PRAGMA foreign_keys = ON;"))

            
            # Check and create default admin user
            with next(self.get_db_session()) as session:
                admin = session.query(User).filter_by(email='admin@gmail.com').first()
                if not admin:
                    admin_password_hash = self.hash_password('admin')
                    admin_user = User(
                        username='admin',
                        email='admin@gmail.com',
                        password_hash=admin_password_hash,
                        is_admin=1,
                        created_at=self.get_current_timestamp()
                    )
                    session.add(admin_user)
                    session.commit()
                    logging.info("Default admin user created.")
            
            logging.info("Database schema initialization complete.")
        except SQLAlchemyError as e:
            logging.error(f"Database initialization failed: {e}")
            raise

    @staticmethod
    def hash_password(password):
        """Hashes a password using passlib's scrypt."""
        return scrypt.hash(password)

    @staticmethod
    def check_password(pwhash, password):
        """Verifies a password against its hash."""
        return scrypt.verify(password, pwhash)

    @staticmethod
    def get_current_timestamp():
        """Returns the current UTC timestamp."""
        return datetime.utcnow()

# Enable foreign key support for all connections
@listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")
    cursor.close()