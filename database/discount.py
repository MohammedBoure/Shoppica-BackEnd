import logging
from datetime import datetime, timedelta
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func
from .base import Database, Discount, DiscountUsage

class DiscountManager(Database):
    """Manages operations for the discounts table in the database using SQLAlchemy."""

    def add_discount(self, code, discount_percent, max_uses=None, expires_at=None, description=None):
        """Adds a new discount."""
        try:
            with next(self.get_db_session()) as session:
                new_discount = Discount(
                    code=code,
                    description=description,
                    discount_percent=discount_percent,
                    max_uses=max_uses,
                    expires_at=expires_at,
                    is_active=1
                )
                session.add(new_discount)
                session.commit()
                discount_id = new_discount.id
                logging.info(f"Discount {code} added with ID: {discount_id}")
                return discount_id
        except SQLAlchemyError as e:
            logging.error(f"Error adding discount {code}: {e}")
            session.rollback()
            return None

    def get_discount_by_id(self, discount_id):
        """Retrieves a discount by its ID."""
        try:
            with next(self.get_db_session()) as session:
                discount = session.query(Discount).filter(Discount.id == discount_id).first()
                logging.info(f"Retrieved discount with ID: {discount_id}")
                return discount
        except SQLAlchemyError as e:
            logging.error(f"Error retrieving discount by ID {discount_id}: {e}")
            return None

    def get_discount_by_code(self, code):
        """Retrieves a discount by its code."""
        try:
            with next(self.get_db_session()) as session:
                discount = session.query(Discount).filter(Discount.code == code).first()
                logging.info(f"Retrieved discount with code: {code}")
                return discount
        except SQLAlchemyError as e:
            logging.error(f"Error retrieving discount by code {code}: {e}")
            return None

    def get_valid_discount(self, code):
        """Retrieves a valid discount by code."""
        try:
            with next(self.get_db_session()) as session:
                current_time = self.get_current_timestamp()
                usage_count_subquery = (
                    session.query(func.count(DiscountUsage.id))
                    .filter(DiscountUsage.discount_id == Discount.id)
                    .scalar_subquery()
                )
                discount = (
                    session.query(Discount)
                    .filter(
                        Discount.code == code,
                        Discount.is_active == 1,
                        func.coalesce(Discount.expires_at, current_time + timedelta(seconds=1)) > current_time,
                        func.coalesce(usage_count_subquery, 0) < func.coalesce(Discount.max_uses, float('inf'))
                    )
                    .first()
                )
                if discount:
                    logging.info(f"Retrieved valid discount with code: {code}")
                else:
                    usage_count = session.query(func.count(DiscountUsage.id)).filter(DiscountUsage.discount_id == discount.id if discount else -1).scalar() or 0
                    logging.info(
                        f"No valid discount found with code: {code}. "
                        f"Reasons: is_active={discount.is_active if discount else 'N/A'}, "
                        f"expires_at={discount.expires_at if discount else 'N/A'}, "
                        f"usage_count={usage_count}, max_uses={discount.max_uses if discount else 'N/A'}"
                    )
                return discount
        except Exception as e:
            logging.error(f"Error retrieving valid discount {code}: {str(e)}", exc_info=True)
            return None

    def update_discount(self, discount_id, code=None, description=None, discount_percent=None, max_uses=None, expires_at=None, is_active=None):
        """Updates discount details. Only provided fields are updated."""
        try:
            with next(self.get_db_session()) as session:
                discount = session.query(Discount).filter(Discount.id == discount_id).first()
                if not discount:
                    logging.warning(f"No discount found with ID: {discount_id}")
                    return False

                if code is not None:
                    discount.code = code
                if description is not None:
                    discount.description = description
                if discount_percent is not None:
                    discount.discount_percent = discount_percent
                if max_uses is not None:
                    discount.max_uses = max_uses
                if expires_at is not None:
                    discount.expires_at = expires_at
                if is_active is not None:
                    discount.is_active = is_active

                session.commit()
                logging.info(f"Updated discount with ID: {discount_id}")
                return True
        except SQLAlchemyError as e:
            logging.error(f"Error updating discount {discount_id}: {e}")
            session.rollback()
            return False

    def delete_discount(self, discount_id):
        """Deletes a discount by its ID."""
        try:
            with next(self.get_db_session()) as session:
                discount = session.query(Discount).filter(Discount.id == discount_id).first()
                if not discount:
                    logging.warning(f"No discount found with ID: {discount_id}")
                    return False

                session.delete(discount)
                session.commit()
                logging.info(f"Deleted discount with ID: {discount_id}")
                return True
        except SQLAlchemyError as e:
            logging.error(f"Error deleting discount {discount_id}: {e}")
            session.rollback()
            return False

    def get_discounts(self, page=1, per_page=20):
        """Retrieves discounts with pagination."""
        try:
            with next(self.get_db_session()) as session:
                total = session.query(func.count(Discount.id)).scalar()
                discounts = (
                    session.query(Discount)
                    .order_by(Discount.id)
                    .limit(per_page)
                    .offset((page - 1) * per_page)
                    .all()
                )
                logging.info(f"Retrieved {len(discounts)} discounts. Total: {total}")
                return discounts, total
        except SQLAlchemyError as e:
            logging.error(f"Error retrieving discounts: {e}")
            return [], 0