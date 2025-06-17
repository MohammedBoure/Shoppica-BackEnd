from .base import Database
import sqlite3
import logging

class AddressManager(Database):
    """Manages operations for the addresses table in the database."""

    def add_address(self, user_id, address_line1, city, country, address_line2=None, state=None, postal_code=None, is_default=0):
        """Adds a new address for a user."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO addresses (user_id, address_line1, address_line2, city, state, postal_code, country, is_default)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (user_id, address_line1, address_line2, city, state, postal_code, country, is_default))
                conn.commit()
                address_id = cursor.lastrowid
                logging.info(f"Address added for user {user_id} with ID: {address_id}")
                return address_id
        except sqlite3.Error as e:
            logging.error(f"Error adding address for user {user_id}: {e}")
            return None

    def get_address_by_id(self, address_id):
        """Retrieves an address by its ID."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM addresses WHERE id = ?', (address_id,))
                address = cursor.fetchone()
                if address:
                    logging.info(f"Retrieved address with ID: {address_id}")
                else:
                    logging.warning(f"Address with ID {address_id} not found.")
                return address
        except sqlite3.Error as e:
            logging.error(f"Error retrieving address by ID {address_id}: {e}")
            return None



    def get_addresses_by_user(self, user_id):
        """Retrieves all addresses for a user."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM addresses WHERE user_id = ?', (user_id,))
                addresses = cursor.fetchall()
                logging.info(f"Retrieved {len(addresses)} addresses for user {user_id}")
                return addresses
        except sqlite3.Error as e:
            logging.error(f"Error retrieving addresses for user {user_id}: {e}")
            return []

    def update_address(self, address_id, address_line1=None, address_line2=None, city=None, state=None, postal_code=None, country=None, is_default=None):
        """Updates address details. Only provided fields are updated."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                updates = []
                params = []
                
                if address_line1 is not None:
                    updates.append('address_line1 = ?')
                    params.append(address_line1)
                if address_line2 is not None:
                    updates.append('address_line2 = ?')
                    params.append(address_line2)
                if city is not None:
                    updates.append('city = ?')
                    params.append(city)
                if state is not None:
                    updates.append('state = ?')
                    params.append(state)
                if postal_code is not None:
                    updates.append('postal_code = ?')
                    params.append(postal_code)
                if country is not None:
                    updates.append('country = ?')
                    params.append(country)
                if is_default is not None:
                    updates.append('is_default = ?')
                    params.append(is_default)
                
                if not updates:
                    logging.info(f"No updates provided for address ID: {address_id}")
                    return True

                params.append(address_id)
                query = f'UPDATE addresses SET {", ".join(updates)} WHERE id = ?'
                cursor.execute(query, params)
                conn.commit()
                if cursor.rowcount > 0:
                    logging.info(f"Updated address with ID: {address_id}")
                    return True
                else:
                    logging.warning(f"No address found with ID: {address_id}")
                    return False
        except sqlite3.Error as e:
            logging.error(f"Error updating address {address_id}: {e}")
            return False

    def delete_address(self, address_id):
        """Deletes an address by its ID."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM addresses WHERE id = ?', (address_id,))
                conn.commit()
                if cursor.rowcount > 0:
                    logging.info(f"Deleted address with ID: {address_id}")
                    return True
                else:
                    logging.warning(f"No address found with ID: {address_id}")
                    return False
        except sqlite3.Error as e:
            logging.error(f"Error deleting address {address_id}: {e}")
            return False

    def get_addresses(self, page=1, per_page=20):
        """Retrieves addresses with pagination."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) as total FROM addresses')
                total = cursor.fetchone()['total']
                cursor.execute('''
                    SELECT * FROM addresses
                    ORDER BY id
                    LIMIT ? OFFSET ?
                ''', (per_page, (page - 1) * per_page))
                addresses = cursor.fetchall()
                logging.info(f"Retrieved {len(addresses)} addresses. Total: {total}")
                return addresses, total
        except sqlite3.Error as e:
            logging.error(f"Error retrieving addresses: {e}")
            return [], 0