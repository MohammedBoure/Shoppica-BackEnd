from .base import Database
import sqlite3
import logging

class ReviewManager(Database):
    """Manages operations for the reviews table in the database."""

    def add_review(self, user_id, product_id, rating, comment=None):
        """Adds a new review for a product."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO reviews (user_id, product_id, rating, comment, created_at)
                    VALUES (?, ?, ?, ?, ?)
                ''', (user_id, product_id, rating, comment, self.get_current_timestamp()))
                conn.commit()
                review_id = cursor.lastrowid
                logging.info(f"Review added for product {product_id} by user {user_id} with ID: {review_id}")
                return review_id
        except sqlite3.Error as e:
            logging.error(f"Error adding review for product {product_id} by user {user_id}: {e}")
            return None

    def get_review_by_id(self, review_id):
        """Retrieves a review by its ID."""
        try:
            with self.get_db_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM reviews WHERE id = ?', (review_id,))
                review = cursor.fetchone()
                if review:
                    review_dict = dict(review)
                    logging.info(f"Retrieved review with ID: {review_id}")
                    return review_dict
                return None
        except sqlite3.Error as e:
            logging.error(f"Error retrieving review by ID {review_id}: {e}")
            return None

    def get_reviews_by_product(self, product_id):
        """Retrieves all reviews for a product."""
        try:
            with self.get_db_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM reviews WHERE product_id = ?', (product_id,))
                reviews = [dict(review) for review in cursor.fetchall()]
                logging.info(f"Retrieved {len(reviews)} reviews for product {product_id}")
                return reviews
        except sqlite3.Error as e:
            logging.error(f"Error retrieving reviews for product {product_id}: {e}")
            return []

    def update_review(self, review_id, rating=None, comment=None):
        """Updates review details. Only provided fields are updated."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                updates = []
                params = []
                
                if rating is not None:
                    updates.append('rating = ?')
                    params.append(rating)
                if comment is not None:
                    updates.append('comment = ?')
                    params.append(comment)
                
                if not updates:
                    logging.info(f"No updates provided for review ID: {review_id}")
                    return True

                params.append(review_id)
                query = f'UPDATE reviews SET {", ".join(updates)} WHERE id = ?'
                cursor.execute(query, params)
                conn.commit()
                if cursor.rowcount > 0:
                    logging.info(f"Updated review with ID: {review_id}")
                    return True
                else:
                    logging.warning(f"No review found with ID: {review_id}")
                    return False
        except sqlite3.Error as e:
            logging.error(f"Error updating review {review_id}: {e}")
            return False

    def delete_review(self, review_id):
        """Deletes a review by its ID."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM reviews WHERE id = ?', (review_id,))
                conn.commit()
                if cursor.rowcount > 0:
                    logging.info(f"Deleted review with ID: {review_id}")
                    return True
                else:
                    logging.warning(f"No review found with ID: {review_id}")
                    return False
        except sqlite3.Error as e:
            logging.error(f"Error deleting review {review_id}: {e}")
            return False

    def get_reviews(self, page=1, per_page=20):
        """Retrieves reviews with pagination."""
        try:
            with self.get_db_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) as total FROM reviews')
                total = cursor.fetchone()['total']
                cursor.execute('''
                    SELECT * FROM reviews
                    ORDER BY created_at DESC
                    LIMIT ? OFFSET ?
                ''', (per_page, (page - 1) * per_page))
                reviews = [dict(review) for review in cursor.fetchall()]
                logging.info(f"Retrieved {len(reviews)} reviews. Total: {total}")
                return reviews, total
        except sqlite3.Error as e:
            logging.error(f"Error retrieving reviews: {e}")
            return [], 0

    def search_reviews(self, product_id=None, user_id=None, min_rating=None, max_rating=None, page=1, per_page=20):
        """Searches reviews based on product_id, user_id, or rating range with pagination."""
        try:
            with self.get_db_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                conditions = []
                params = []

                if product_id is not None:
                    conditions.append('product_id = ?')
                    params.append(product_id)
                if user_id is not None:
                    conditions.append('user_id = ?')
                    params.append(user_id)
                if min_rating is not None:
                    conditions.append('rating >= ?')
                    params.append(min_rating)
                if max_rating is not None:
                    conditions.append('rating <= ?')
                    params.append(max_rating)

                where_clause = ' WHERE ' + ' AND '.join(conditions) if conditions else ''
                
                # Count total reviews matching the criteria
                count_query = f'SELECT COUNT(*) as total FROM reviews{where_clause}'
                cursor.execute(count_query, params)
                total = cursor.fetchone()['total']

                # Fetch reviews with pagination
                query = f'''
                    SELECT * FROM reviews{where_clause}
                    ORDER BY created_at DESC
                    LIMIT ? OFFSET ?
                '''
                params.extend([per_page, (page - 1) * per_page])
                cursor.execute(query, params)
                reviews = [dict(review) for review in cursor.fetchall()]
                logging.info(f"Found {len(reviews)} reviews matching search criteria. Total: {total}")
                return reviews, total
        except sqlite3.Error as e:
            logging.error(f"Error searching reviews: {e}")
            return [], 0

    def delete_reviews_by_product(self, product_id):
        """Deletes all reviews for a specific product."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM reviews WHERE product_id = ?', (product_id,))
                conn.commit()
                deleted_count = cursor.rowcount
                logging.info(f"Deleted {deleted_count} reviews for product {product_id}")
                return deleted_count
        except sqlite3.Error as e:
            logging.error(f"Error deleting reviews for product {product_id}: {e}")
            return 0

    def delete_reviews_by_user(self, user_id):
        """Deletes all reviews by a specific user."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM reviews WHERE user_id = ?', (user_id,))
                conn.commit()
                deleted_count = cursor.rowcount
                logging.info(f"Deleted {deleted_count} reviews by user {user_id}")
                return deleted_count
        except sqlite3.Error as e:
            logging.error(f"Error deleting reviews for user {user_id}: {e}")
            return 0

    def get_product_review_stats(self, product_id):
        """Returns statistics about reviews for a specific product."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT 
                        COUNT(*) as total_reviews,
                        AVG(rating) as average_rating,
                        SUM(CASE WHEN rating = 1 THEN 1 ELSE 0 END) as rating_1,
                        SUM(CASE WHEN rating = 2 THEN 1 ELSE 0 END) as rating_2,
                        SUM(CASE WHEN rating = 3 THEN 1 ELSE 0 END) as rating_3,
                        SUM(CASE WHEN rating = 4 THEN 1 ELSE 0 END) as rating_4,
                        SUM(CASE WHEN rating = 5 THEN 1 ELSE 0 END) as rating_5
                    FROM reviews
                    WHERE product_id = ?
                ''', (product_id,))
                stats = cursor.fetchone()
                if stats:
                    stats_dict = {
                        'total_reviews': stats['total_reviews'],
                        'average_rating': round(stats['average_rating'], 2) if stats['average_rating'] else 0.0,
                        'rating_distribution': {
                            '1': stats['rating_1'],
                            '2': stats['rating_2'],
                            '3': stats['rating_3'],
                            '4': stats['rating_4'],
                            '5': stats['rating_5']
                        }
                    }
                    logging.info(f"Retrieved review stats for product {product_id}: {stats_dict}")
                    return stats_dict
                return {'total_reviews': 0, 'average_rating': 0.0, 'rating_distribution': {'1': 0, '2': 0, '3': 0, '4': 0, '5': 0}}
        except sqlite3.Error as e:
            logging.error(f"Error retrieving review stats for product {product_id}: {e}")
            return {'total_reviews': 0, 'average_rating': 0.0, 'rating_distribution': {'1': 0, '2': 0, '3': 0, '4': 0, '5': 0}}

    def get_overall_review_stats(self):
        """Returns overall statistics for all reviews."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT 
                        COUNT(*) as total_reviews,
                        AVG(rating) as average_rating,
                        SUM(CASE WHEN rating = 1 THEN 1 ELSE 0 END) as rating_1,
                        SUM(CASE WHEN rating = 2 THEN 1 ELSE 0 END) as rating_2,
                        SUM(CASE WHEN rating = 3 THEN 1 ELSE 0 END) as rating_3,
                        SUM(CASE WHEN rating = 4 THEN 1 ELSE 0 END) as rating_4,
                        SUM(CASE WHEN rating = 5 THEN 1 ELSE 0 END) as rating_5
                    FROM reviews
                ''')
                stats = cursor.fetchone()
                if stats:
                    stats_dict = {
                        'total_reviews': stats['total_reviews'],
                        'average_rating': round(stats['average_rating'], 2) if stats['average_rating'] else 0.0,
                        'rating_distribution': {
                            '1': stats['rating_1'],
                            '2': stats['rating_2'],
                            '3': stats['rating_3'],
                            '4': stats['rating_4'],
                            '5': stats['rating_5']
                        }
                    }
                    logging.info(f"Retrieved overall review stats: {stats_dict}")
                    return stats_dict
                return {'total_reviews': 0, 'average_rating': 0.0, 'rating_distribution': {'1': 0, '2': 0, '3': 0, '4': 0, '5': 0}}
        except sqlite3.Error as e:
            logging.error(f"Error retrieving overall review stats: {e}")
            return {'total_reviews': 0, 'average_rating': 0.0, 'rating_distribution': {'1': 0, '2': 0, '3': 0, '4': 0, '5': 0}}