import logging
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func, distinct, or_



from .base import Database, Address, User 

class AddressManager:
    """Manages address operations using SQLAlchemy ORM."""

    def __init__(self):
        """Initialize with a database instance."""
        self.db = Database()

    def add_address(self, user_id: int, address_line: str, city: str, state: str, postal_code: str, is_default: int = 0):
        """
        Adds a new address for a user and manages the default status.

        Args:
            user_id (int): The ID of the user.
            address_line (str): The main address line.
            city (str): The city.
            state (str): The state or province.
            postal_code (str): The postal code.
            is_default (int): 1 if this is the default address, 0 otherwise.

        Returns:
            Address | None: The newly created Address object or None on failure.
        """
        session_generator = self.db.get_db_session()
        session = next(session_generator)
        try:
            if is_default == 1:
                # Reset existing default address for the user
                session.query(Address).filter_by(user_id=user_id, is_default=1).update({"is_default": 0})

            new_address = Address(
                user_id=user_id,
                address_line=address_line,
                city=city,
                state=state,
                postal_code=postal_code,
                is_default=is_default
            )
            session.add(new_address)
            session.commit()
            session.refresh(new_address)
            logging.info(f"Address added for user {user_id} with ID: {new_address.id}")
            return new_address
        except SQLAlchemyError as e:
            session.rollback()
            logging.error(f"Error adding address for user {user_id}: {e}")
            return None
        finally:
            session.close()

    def get_address_by_id(self, address_id: int):
        """Retrieves an address by its ID."""
        with next(self.db.get_db_session()) as session:
            try:
                address = session.query(Address).filter_by(id=address_id).first()
                if address:
                    logging.info(f"Retrieved address with ID: {address_id}")
                    return address
                else:
                    logging.warning(f"Address with ID {address_id} not found.")
                    return None
            except SQLAlchemyError as e:
                logging.error(f"Error retrieving address by ID {address_id}: {e}")
                return None

    def get_addresses_by_user(self, user_id: int):
        """Retrieves all addresses for a user."""
        with next(self.db.get_db_session()) as session:
            try:
                addresses = session.query(Address).filter_by(user_id=user_id).all()
                logging.info(f"Retrieved {len(addresses)} addresses for user {user_id}")
                return addresses
            except SQLAlchemyError as e:
                logging.error(f"Error retrieving addresses for user {user_id}: {e}")
                return []

    def update_address(self, address_id: int, **kwargs):
        """
        Updates address details. Only provided fields are updated.
        
        Args:
            address_id (int): The ID of the address to update.
            **kwargs: Fields to update (e.g., address_line, city, is_default).
        """
        with next(self.db.get_db_session()) as session:
            try:
                address = session.query(Address).filter_by(id=address_id).first()
                if not address:
                    logging.warning(f"No address found with ID: {address_id}")
                    return False

                # If setting this address as default, unset the old default first
                if kwargs.get('is_default') == 1:
                    session.query(Address).filter(
                        Address.user_id == address.user_id, 
                        Address.id != address_id
                    ).update({"is_default": 0})
                
                # Update fields from kwargs
                for key, value in kwargs.items():
                    if hasattr(address, key) and value is not None:
                        setattr(address, key, value)
                
                session.commit()
                logging.info(f"Updated address with ID: {address_id}")
                return True
            except SQLAlchemyError as e:
                session.rollback()
                logging.error(f"Error updating address {address_id}: {e}")
                return False

    def delete_address(self, address_id: int):
        """Deletes an address by its ID."""
        with next(self.db.get_db_session()) as session:
            try:
                address = session.query(Address).filter_by(id=address_id).first()
                if address:
                    session.delete(address)
                    session.commit()
                    logging.info(f"Deleted address with ID: {address_id}")
                    return True
                else:
                    logging.warning(f"No address found with ID: {address_id}")
                    return False
            except SQLAlchemyError as e:
                session.rollback()
                logging.error(f"Error deleting address {address_id}: {e}")
                return False

    def delete_addresses_by_user(self, user_id: int):
        """
        Deletes all addresses associated with a specific user.

        Args:
            user_id (int): The ID of the user whose addresses will be deleted.

        Returns:
            int: The number of deleted addresses.
        """
        with next(self.db.get_db_session()) as session:
            try:
                deleted_count = session.query(Address).filter_by(user_id=user_id).delete()
                session.commit()
                logging.info(f"Deleted {deleted_count} addresses for user {user_id}")
                return deleted_count
            except SQLAlchemyError as e:
                session.rollback()
                logging.error(f"Error deleting addresses for user {user_id}: {e}")
                return 0

    def get_addresses(self, page: int = 1, per_page: int = 20):
        """Retrieves addresses with pagination."""
        with next(self.db.get_db_session()) as session:
            try:
                query = session.query(Address)
                total = query.count()
                addresses = query.order_by(Address.id).offset((page - 1) * per_page).limit(per_page).all()
                logging.info(f"Retrieved {len(addresses)} addresses. Total: {total}")
                return addresses, total
            except SQLAlchemyError as e:
                logging.error(f"Error retrieving addresses: {e}")
                return [], 0

    def get_default_address(self, user_id: int):
        """Retrieves the default address for a user."""
        with next(self.db.get_db_session()) as session:
            try:
                address = session.query(Address).filter_by(user_id=user_id, is_default=1).first()
                if address:
                    logging.info(f"Retrieved default address for user {user_id}")
                    return address
                logging.warning(f"No default address found for user {user_id}")
                return None
            except SQLAlchemyError as e:
                logging.error(f"Error retrieving default address for user {user_id}: {e}")
                return None
    
    def get_address_stats(self):
        """Returns statistics about addresses using SQLAlchemy."""
        with next(self.db.get_db_session()) as session:
            try:
                total_addresses = session.query(func.count(Address.id)).scalar()
                default_addresses = session.query(func.count(Address.id)).filter_by(is_default=1).scalar()
                users_with_addresses = session.query(func.count(distinct(Address.user_id))).scalar()
                
                stats = {
                    'total_addresses': total_addresses,
                    'default_addresses': default_addresses,
                    'users_with_addresses': users_with_addresses
                }
                logging.info(f"Retrieved address stats: {stats}")
                return stats
            except SQLAlchemyError as e:
                logging.error(f"Error retrieving address stats: {e}")
                return {'total_addresses': 0, 'default_addresses': 0, 'users_with_addresses': 0}
    
   

    def search_addresses(self, query_word: str = None, page: int = 1, per_page: int = 20):
        """
        Searches for addresses using a single keyword across multiple fields (city, state, postal_code).
        Uses case-insensitive partial matching.

        Args:
            query_word (str, optional): The word to search for.
            page (int): Page number.
            per_page (int): Results per page.

        Returns:
            tuple[list[Address], int]: List of matching addresses and total count.
        """
        with next(self.db.get_db_session()) as session:
            try:
                query = session.query(Address)

                if query_word:
                    like_pattern = f"%{query_word}%"
                    query = query.filter(
                        or_(
                            Address.city.ilike(like_pattern),
                            Address.state.ilike(like_pattern),
                            Address.postal_code.ilike(like_pattern),
                            Address.address_line.ilike(like_pattern)
                        )
                    )

                total = query.count()
                addresses = query.order_by(Address.id).offset((page - 1) * per_page).limit(per_page).all()
                
                logging.info(f"Search returned {total} results for query '{query_word}' on page {page}")
                return addresses, total
            except SQLAlchemyError as e:
                logging.error(f"Error searching addresses with query '{query_word}': {e}")
                return [], 0

            
    def get_user_address_stats(self, user_id: int):
        """Returns statistics for addresses of a specific user."""
        with next(self.db.get_db_session()) as session:
            try:
                total = session.query(func.count(Address.id)).filter_by(user_id=user_id).scalar()
                default_count = session.query(func.count(Address.id)).filter_by(user_id=user_id, is_default=1).scalar()

                stats = {
                    'total_addresses': total,
                    'default_addresses': default_count
                }
                logging.info(f"Retrieved address stats for user {user_id}: {stats}")
                return stats
            except SQLAlchemyError as e:
                logging.error(f"Error retrieving user address stats for user {user_id}: {e}")
                return {'total_addresses': 0, 'default_addresses': 0}
    