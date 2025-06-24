from .base import Database
import sqlite3
import logging

class AddressManager(Database):
    """Manages operations for the addresses table in the database."""

    def add_address(self, user_id, address_line1, city, country, address_line2=None, state=None, postal_code=None, is_default=0):
        """Adds a new address for a user and manages default status."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                if is_default == 1:
                    # Reset existing default address for the user
                    cursor.execute('UPDATE addresses SET is_default = 0 WHERE user_id = ?', (user_id,))
                
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
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM addresses WHERE id = ?', (address_id,))
                address = cursor.fetchone()
                if address:
                    address_dict = dict(address)
                    logging.info(f"Retrieved address with ID: {address_id}")
                    return address_dict
                else:
                    logging.warning(f"Address with ID {address_id} not found.")
                    return None
        except sqlite3.Error as e:
            logging.error(f"Error retrieving address by ID {address_id}: {e}")
            return None

    def get_addresses_by_user(self, user_id):
        """Retrieves all addresses for a user."""
        try:
            with self.get_db_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM addresses WHERE user_id = ?', (user_id,))
                addresses = [dict(address) for address in cursor.fetchall()]
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
                if is_default == 1:
                    # Get user_id of the address to reset other defaults
                    cursor.execute('SELECT user_id FROM addresses WHERE id = ?', (address_id,))
                    user_id = cursor.fetchone()
                    if user_id:
                        cursor.execute('UPDATE addresses SET is_default = 0 WHERE user_id = ?', (user_id['user_id'],))

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
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) as total FROM addresses')
                total = cursor.fetchone()['total']
                cursor.execute('''
                    SELECT * FROM addresses
                    ORDER BY id
                    LIMIT ? OFFSET ?
                ''', (per_page, (page - 1) * per_page))
                addresses = [dict(address) for address in cursor.fetchall()]
                logging.info(f"Retrieved {len(addresses)} addresses. Total: {total}")
                return addresses, total
        except sqlite3.Error as e:
            logging.error(f"Error retrieving addresses: {e}")
            return [], 0

    def search_addresses(self, user_id=None, city=None, country=None, page=1, per_page=20):
        """Searches addresses based on user_id, city, or country with pagination."""
        try:
            with self.get_db_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                conditions = []
                params = []

                if user_id is not None:
                    conditions.append('user_id = ?')
                    params.append(user_id)
                if city is not None:
                    conditions.append('city LIKE ?')
                    params.append(f'%{city}%')
                if country is not None:
                    conditions.append('country LIKE ?')
                    params.append(f'%{country}%')

                where_clause = ' WHERE ' + ' AND '.join(conditions) if conditions else ''
                
                # Count total addresses matching the criteria
                count_query = f'SELECT COUNT(*) as total FROM addresses{where_clause}'
                cursor.execute(count_query, params)
                total = cursor.fetchone()['total']

                # Fetch addresses with pagination
                query = f'''
                    SELECT * FROM addresses{where_clause}
                    ORDER BY id
                    LIMIT ? OFFSET ?
                '''
                params.extend([per_page, (page - 1) * per_page])
                cursor.execute(query, params)
                addresses = [dict(address) for address in cursor.fetchall()]
                logging.info(f"Found {len(addresses)} addresses matching search criteria. Total: {total}")
                return addresses, total
        except sqlite3.Error as e:
            logging.error(f"Error searching addresses: {e}")
            return [], 0

    def delete_addresses_by_user(self, user_id):
        """Deletes all addresses for a specific user."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM addresses WHERE user_id = ?', (user_id,))
                conn.commit()
                deleted_count = cursor.rowcount
                logging.info(f"Deleted {deleted_count} addresses for user {user_id}")
                return deleted_count
        except sqlite3.Error as e:
            logging.error(f"Error deleting addresses for user {user_id}: {e}")
            return 0

    def get_address_stats(self):
        """Returns statistics about addresses."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) as total_addresses FROM addresses')
                total_addresses = cursor.fetchone()['total_addresses']
                cursor.execute('SELECT COUNT(*) as default_addresses FROM addresses WHERE is_default = 1')
                default_addresses = cursor.fetchone()['default_addresses']
                cursor.execute('SELECT COUNT(DISTINCT user_id) as users_with_addresses FROM addresses')
                users_with_addresses = cursor.fetchone()['users_with_addresses']
                stats = {
                    'total_addresses': total_addresses,
                    'default_addresses': default_addresses,
                    'users_with_addresses': users_with_addresses
                }
                logging.info(f"Retrieved address stats: {stats}")
                return stats
        except sqlite3.Error as e:
            logging.error(f"Error retrieving address stats: {e}")
            return {'total_addresses': 0, 'default_addresses': 0, 'users_with_addresses': 0}

    def get_user_address_stats(self, user_id):
        """Returns address statistics for a specific user."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) as total_addresses FROM addresses WHERE user_id = ?', (user_id,))
                total_addresses = cursor.fetchone()['total_addresses']
                cursor.execute('SELECT COUNT(*) as default_addresses FROM addresses WHERE user_id = ? AND is_default = 1', (user_id,))
                default_addresses = cursor.fetchone()['default_addresses']
                stats = {
                    'total_addresses': total_addresses,
                    'default_addresses': default_addresses
                }
                logging.info(f"Retrieved address stats for user {user_id}: {stats}")
                return stats
        except sqlite3.Error as e:
            logging.error(f"Error retrieving address stats for user {user_id}: {e}")
            return {'total_addresses': 0, 'default_addresses': 0}

    def get_default_address(self, user_id):
        """Retrieves the default address for a user."""
        try:
            with self.get_db_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM addresses WHERE user_id = ? AND is_default = 1', (user_id,))
                address = cursor.fetchone()
                if address:
                    address_dict = dict(address)
                    logging.info(f"Retrieved default address for user {user_id}")
                    return address_dict
                logging.warning(f"No default address found for user {user_id}")
                return None
        except sqlite3.Error as e:
            logging.error(f"Error retrieving default address for user {user_id}: {e}")
            return None