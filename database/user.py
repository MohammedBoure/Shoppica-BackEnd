from .base import Database
import sqlite3
import logging

class UserManager(Database):
    """Manages operations for the users table in the database."""

    def add_user(self, username, email, password, full_name=None, phone_number=None, is_admin=0):
        """Adds a new user to the database with hashed password."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                password_hash = self.hash_password(password)
                cursor.execute('''
                    INSERT INTO users (username, email, password_hash, full_name, phone_number, is_admin, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (username, email, password_hash, full_name, phone_number, is_admin, self.get_current_timestamp()))
                conn.commit()
                user_id = cursor.lastrowid
                logging.info(f"User {username} added with ID: {user_id}")
                return user_id
        except sqlite3.Error as e:
            logging.error(f"Error adding user {username}: {e}")
            return None

    def get_user_by_id(self, user_id):
        """Retrieves a user by their ID."""
        try:
            with self.get_db_connection() as conn:
                conn.row_factory = sqlite3.Row  # هذا يجعل النتائج dict-like
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
                user = cursor.fetchone()
                if user:
                    user_dict = dict(user)  # تحويل row إلى dict عادي
                    logging.info(f"Retrieved user with ID: {user_id}")
                    return user_dict
                return None
        except sqlite3.Error as e:
            logging.error(f"Error retrieving user by ID {user_id}: {e}")
            return None


    def get_user_by_email(self, email):
        """Retrieves a user by their email."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
                user = cursor.fetchone()
                logging.info(f"Retrieved user with email: {email}")
                return user
        except sqlite3.Error as e:
            logging.error(f"Error retrieving user by email {email}: {e}")
            return None

    def get_user_by_username(self, username):
        """Retrieves a user by their username."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
                user = cursor.fetchone()
                logging.info(f"Retrieved user with username: {username}")
                return user
        except sqlite3.Error as e:
            logging.error(f"Error retrieving user by username {username}: {e}")
            return None

    def update_user(self, user_id, full_name=None, phone_number=None, is_admin=None, password=None):
        """Updates user details. Only provided fields are updated."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                updates = []
                params = []
                
                if full_name is not None:
                    updates.append('full_name = ?')
                    params.append(full_name)
                if phone_number is not None:
                    updates.append('phone_number = ?')
                    params.append(phone_number)
                if is_admin is not None:
                    updates.append('is_admin = ?')
                    params.append(is_admin)
                if password is not None:
                    updates.append('password_hash = ?')
                    params.append(self.hash_password(password))
                
                if not updates:
                    logging.info(f"No updates provided for user ID: {user_id}")
                    return True

                params.append(user_id)
                query = f'UPDATE users SET {", ".join(updates)} WHERE id = ?'
                cursor.execute(query, params)
                conn.commit()
                if cursor.rowcount > 0:
                    logging.info(f"Updated user with ID: {user_id}")
                    return True
                else:
                    logging.warning(f"No user found with ID: {user_id}")
                    return False
        except sqlite3.Error as e:
            logging.error(f"Error updating user {user_id}: {e}")
            return False

    def delete_user(self, user_id):
        """Deletes a user by their ID."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
                conn.commit()
                if cursor.rowcount > 0:
                    logging.info(f"Deleted user with ID: {user_id}")
                    return True
                else:
                    logging.warning(f"No user found with ID: {user_id}")
                    return False
        except sqlite3.Error as e:
            logging.error(f"Error deleting user {user_id}: {e}")
            return False

    def get_users(self, page=1, per_page=20):
        """Retrieves users with pagination."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) as total FROM users')
                total = cursor.fetchone()['total']
                cursor.execute('''
                    SELECT * FROM users
                    ORDER BY created_at DESC
                    LIMIT ? OFFSET ?
                ''', (per_page, (page - 1) * per_page))
                users = cursor.fetchall()
                logging.info(f"Retrieved {len(users)} users. Total: {total}")
                return users, total
        except sqlite3.Error as e:
            logging.error(f"Error retrieving users: {e}")
            return [], 0

    def validate_password(self, user_id, password):
        """Validates a user's password."""
        try:
            user = self.get_user_by_id(user_id)
            if user and self.check_password(user['password_hash'], password):
                logging.info(f"Password validated for user ID: {user_id}")
                return True
            logging.warning(f"Invalid password for user ID: {user_id}")
            return False
        except sqlite3.Error as e:
            logging.error(f"Error validating password for user {user_id}: {e}")
            return False

    def clear_all_users(self):
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM users")
                conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Error clearing users: {e}")
