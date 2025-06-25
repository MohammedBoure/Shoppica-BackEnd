from .base import Database, User
import logging
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError

class UserManager(Database):
    """Manages operations for the users table in the database using SQLAlchemy."""

    def add_user(self, username, email, password, full_name=None, phone_number=None, is_admin=0):
        """Adds a new user to the database with hashed password."""
        try:
            with next(self.get_db_session()) as session:
                # Check if username or email already exists
                if session.query(User).filter((User.username == username) | (User.email == email)).first():
                    logging.warning(f"User with username {username} or email {email} already exists.")
                    return None

                password_hash = self.hash_password(password)
                new_user = User(
                    username=username,
                    email=email,
                    password_hash=password_hash,
                    full_name=full_name,
                    phone_number=phone_number,
                    is_admin=is_admin,
                    created_at=self.get_current_timestamp()
                )
                session.add(new_user)
                session.commit()
                user_id = new_user.id
                logging.info(f"User {username} added with ID: {user_id}")
                return user_id
        except SQLAlchemyError as e:
            logging.error(f"Error adding user {username}: {e}")
            session.rollback()
            return None

    def get_user_by_id(self, user_id):
        """Retrieves a user by their ID."""
        try:
            with next(self.get_db_session()) as session:
                user = session.query(User).filter_by(id=user_id).first()
                if user:
                    # Convert to dictionary for consistency
                    user_dict = {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'password_hash': user.password_hash,
                        'full_name': user.full_name,
                        'phone_number': user.phone_number,
                        'is_admin': user.is_admin,
                        'created_at': user.created_at
                    }
                    logging.info(f"Retrieved user with ID: {user_id}")
                    return user_dict
                logging.warning(f"No user found with ID: {user_id}")
                return None
        except SQLAlchemyError as e:
            logging.error(f"Error retrieving user by ID {user_id}: {e}")
            return None

    def get_user_by_email(self, email):
        """Retrieves a user by their email."""
        try:
            with next(self.get_db_session()) as session:
                user = session.query(User).filter_by(email=email).first()
                if user:
                    user_dict = {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'password_hash': user.password_hash,
                        'full_name': user.full_name,
                        'phone_number': user.phone_number,
                        'is_admin': user.is_admin,
                        'created_at': user.created_at
                    }
                    logging.info(f"Retrieved user with email: {email}")
                    return user_dict
                logging.warning(f"No user found with email: {email}")
                return None
        except SQLAlchemyError as e:
            logging.error(f"Error retrieving user by email {email}: {e}")
            return None

    def get_user_by_username(self, username):
        """Retrieves a user by their username."""
        try:
            with next(self.get_db_session()) as session:
                user = session.query(User).filter_by(username=username).first()
                if user:
                    user_dict = {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'password_hash': user.password_hash,
                        'full_name': user.full_name,
                        'phone_number': user.phone_number,
                        'is_admin': user.is_admin,
                        'created_at': user.created_at
                    }
                    logging.info(f"Retrieved user with username: {username}")
                    return user_dict
                logging.warning(f"No user found with username: {username}")
                return None
        except SQLAlchemyError as e:
            logging.error(f"Error retrieving user by username {username}: {e}")
            return None

    def update_user(self, user_id, full_name=None, phone_number=None, is_admin=None, password=None):
        """Updates user details. Only provided fields are updated."""
        try:
            with next(self.get_db_session()) as session:
                user = session.query(User).filter_by(id=user_id).first()
                if not user:
                    logging.warning(f"No user found with ID: {user_id}")
                    return False

                if full_name is not None:
                    user.full_name = full_name
                if phone_number is not None:
                    user.phone_number = phone_number
                if is_admin is not None:
                    user.is_admin = is_admin
                if password is not None:
                    user.password_hash = self.hash_password(password)

                session.commit()
                logging.info(f"Updated user with ID: {user_id}")
                return True
        except SQLAlchemyError as e:
            logging.error(f"Error updating user {user_id}: {e}")
            session.rollback()
            return False

    def delete_user(self, user_id):
        """Deletes a user by their ID."""
        try:
            with next(self.get_db_session()) as session:
                user = session.query(User).filter_by(id=user_id).first()
                if not user:
                    logging.warning(f"No user found with ID: {user_id}")
                    return False
                session.delete(user)
                session.commit()
                logging.info(f"Deleted user with ID: {user_id}")
                return True
        except SQLAlchemyError as e:
            logging.error(f"Error deleting user {user_id}: {e}")
            session.rollback()
            return False

    def get_users(self, page=1, per_page=20):
        """Retrieves users with pagination."""
        try:
            with next(self.get_db_session()) as session:
                total = session.query(func.count(User.id)).scalar()
                users = session.query(User).order_by(User.created_at.desc())\
                    .limit(per_page).offset((page - 1) * per_page).all()
                users_list = [{
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'password_hash': user.password_hash,
                    'full_name': user.full_name,
                    'phone_number': user.phone_number,
                    'is_admin': user.is_admin,
                    'created_at': user.created_at
                } for user in users]
                logging.info(f"Retrieved {len(users_list)} users. Total: {total}")
                return users_list, total
        except SQLAlchemyError as e:
            logging.error(f"Error retrieving users: {e}")
            return [], 0

    def validate_password(self, user_id, password):
        """Validates a user's password."""
        try:
            with next(self.get_db_session()) as session:
                user = session.query(User).filter_by(id=user_id).first()
                if user and self.check_password(user.password_hash, password):
                    logging.info(f"Password validated for user ID: {user_id}")
                    return True
                logging.warning(f"Invalid password for user ID: {user_id}")
                return False
        except SQLAlchemyError as e:
            logging.error(f"Error validating password for user {user_id}: {e}")
            return False

    def clear_all_users(self):
        """Clears all users from the database."""
        try:
            with next(self.get_db_session()) as session:
                session.query(User).delete()
                session.commit()
                logging.info("All users cleared from database.")
        except SQLAlchemyError as e:
            logging.error(f"Error clearing users: {e}")
            session.rollback()

    def search_users(self, query, page=1, per_page=20):
        """Searches users by username or email (partial match)."""
        try:
            with next(self.get_db_session()) as session:
                search_term = f'%{query}%'
                total = session.query(func.count(User.id))\
                    .filter((User.username.ilike(search_term)) | (User.email.ilike(search_term))).scalar()
                users = session.query(User)\
                    .filter((User.username.ilike(search_term)) | (User.email.ilike(search_term)))\
                    .order_by(User.created_at.desc())\
                    .limit(per_page).offset((page - 1) * per_page).all()
                users_list = [{
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'password_hash': user.password_hash,
                    'full_name': user.full_name,
                    'phone_number': user.phone_number,
                    'is_admin': user.is_admin,
                    'created_at': user.created_at
                } for user in users]
                logging.info(f"Found {len(users_list)} users matching query: {query}")
                return users_list, total
        except SQLAlchemyError as e:
            logging.error(f"Error searching users with query {query}: {e}")
            return [], 0