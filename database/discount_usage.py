from .base import Database, DiscountUsage, User, Discount
from sqlalchemy.exc import SQLAlchemyError
import logging

class DiscountUsageManager(Database):
    """Manages operations for the discount_usage table in the database."""

    def add_discount_usage(self, discount_id, user_id):
        """Records a discount usage by a user."""
        try:
            with next(self.get_db_session()) as session:
                discount_usage = DiscountUsage(
                    discount_id=discount_id,
                    user_id=user_id,
                    used_at=self.get_current_timestamp()
                )
                session.add(discount_usage)
                session.commit()
                usage_id = discount_usage.id
                logging.info(f"Discount usage added for discount {discount_id} by user {user_id} with ID: {usage_id}")
                return usage_id
        except SQLAlchemyError as e:
            logging.error(f"Error adding discount usage for discount {discount_id}, user {user_id}: {e}")
            return None

    def get_discount_usage_by_id(self, usage_id):
        """Retrieves a discount usage by its ID."""
        try:
            with next(self.get_db_session()) as session:
                usage = session.query(DiscountUsage).filter_by(id=usage_id).first()
                if usage:
                    logging.info(f"Retrieved discount usage with ID: {usage_id}")
                    return usage
                else:
                    logging.warning(f"No discount usage found with ID: {usage_id}")
                    return None
        except SQLAlchemyError as e:
            logging.error(f"Error retrieving discount usage by ID {usage_id}: {e}")
            return None

    def get_discount_usages_by_discount(self, discount_id):
        """Retrieves all usages for a discount."""
        try:
            with next(self.get_db_session()) as session:
                usages = session.query(DiscountUsage).filter_by(discount_id=discount_id).all()
                logging.info(f"Retrieved {len(usages)} discount usages for discount {discount_id}")
                return usages
        except SQLAlchemyError as e:
            logging.error(f"Error retrieving discount usages for discount {discount_id}: {e}")
            return []

    def get_discount_usages_by_user(self, user_id):
        """Retrieves all discount usages for a user."""
        try:
            with next(self.get_db_session()) as session:
                usages = session.query(DiscountUsage).filter_by(user_id=user_id).all()
                logging.info(f"Retrieved {len(usages)} discount usages for user {user_id}")
                return usages
        except SQLAlchemyError as e:
            logging.error(f"Error retrieving discount usages for user {user_id}: {e}")
            return []

    def delete_discount_usage(self, usage_id):
        """Deletes a discount usage by its ID."""
        try:
            with next(self.get_db_session()) as session:
                usage = session.query(DiscountUsage).filter_by(id=usage_id).first()
                if usage:
                    session.delete(usage)
                    session.commit()
                    logging.info(f"Deleted discount usage with ID: {usage_id}")
                    return True
                else:
                    logging.warning(f"No discount usage found with ID: {usage_id}")
                    return False
        except SQLAlchemyError as e:
            logging.error(f"Error deleting discount usage {usage_id}: {e}")
            return False

    def get_discount_usages(self, page=1, per_page=20):
        """Retrieves discount usages with pagination."""
        try:
            with next(self.get_db_session()) as session:
                total = session.query(DiscountUsage).count()
                usages = (
                    session.query(DiscountUsage, Discount.code)
                    .join(Discount, DiscountUsage.discount_id == Discount.id)
                    .order_by(DiscountUsage.used_at.desc())
                    .limit(per_page)
                    .offset((page - 1) * per_page)
                    .all()
                )
                # Convert query results to a list of tuples for compatibility with original return format
                result = [(usage, discount_code) for usage, discount_code in usages]
                logging.info(f"Retrieved {len(result)} discount usages. Total: {total}")
                return result, total
        except SQLAlchemyError as e:
            logging.error(f"Error retrieving discount usages: {e}")
            return [], 0