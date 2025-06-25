import logging
from datetime import datetime
from sqlalchemy import and_, func
from sqlalchemy.exc import SQLAlchemyError
from .base import Database, CategoryDiscount, Category

class CategoryDiscountManager(Database):
    """Manages operations for the category_discounts table in the database using SQLAlchemy ORM."""

    def add_category_discount(self, category_id, discount_percent, starts_at=None, ends_at=None, is_active=1):
        """Adds a new category discount."""
        try:
            with next(self.get_db_session()) as session:
                new_discount = CategoryDiscount(
                    category_id=category_id,
                    discount_percent=discount_percent,
                    starts_at=starts_at,
                    ends_at=ends_at,
                    is_active=is_active
                )
                session.add(new_discount)
                session.commit()
                discount_id = new_discount.id
                logging.info(f"Category discount added for category {category_id} with ID: {discount_id}")
                return discount_id
        except SQLAlchemyError as e:
            logging.error(f"Error adding category discount: {e}")
            return None

    def get_category_discount_by_id(self, discount_id):
        """Retrieves a category discount by its ID."""
        try:
            with next(self.get_db_session()) as session:
                discount = session.query(CategoryDiscount, Category.name).join(
                    Category, CategoryDiscount.category_id == Category.id
                ).filter(CategoryDiscount.id == discount_id).first()
                if discount:
                    discount_dict = {
                        'id': discount.CategoryDiscount.id,
                        'category_id': discount.CategoryDiscount.category_id,
                        'discount_percent': discount.CategoryDiscount.discount_percent,
                        'starts_at': discount.CategoryDiscount.starts_at,
                        'ends_at': discount.CategoryDiscount.ends_at,
                        'is_active': discount.CategoryDiscount.is_active,
                        'category_name': discount.name
                    }
                    logging.info(f"Retrieved category discount with ID: {discount_id}")
                    return discount_dict
                logging.warning(f"No category discount found with ID: {discount_id}")
                return None
        except SQLAlchemyError as e:
            logging.error(f"Error retrieving category discount by ID {discount_id}: {e}")
            return None

    def get_category_discounts_by_category(self, category_id):
        """Retrieves all discounts for a category."""
        try:
            with next(self.get_db_session()) as session:
                discounts = session.query(CategoryDiscount, Category.name).join(
                    Category, CategoryDiscount.category_id == Category.id
                ).filter(CategoryDiscount.category_id == category_id).all()
                discount_list = [
                    {
                        'id': d.CategoryDiscount.id,
                        'category_id': d.CategoryDiscount.category_id,
                        'discount_percent': d.CategoryDiscount.discount_percent,
                        'starts_at': d.CategoryDiscount.starts_at,
                        'ends_at': d.CategoryDiscount.ends_at,
                        'is_active': d.CategoryDiscount.is_active,
                        'category_name': d.name
                    } for d in discounts
                ]
                logging.info(f"Retrieved {len(discount_list)} category discounts for category {category_id}")
                return discount_list
        except SQLAlchemyError as e:
            logging.error(f"Error retrieving category discounts for category {category_id}: {e}")
            return []

    def get_valid_category_discounts(self, category_id):
        """Retrieves valid (active and within date range) discounts for a category."""
        try:
            with next(self.get_db_session()) as session:
                current_time = self.get_current_timestamp()
                discounts = session.query(CategoryDiscount, Category.name).join(
                    Category, CategoryDiscount.category_id == Category.id
                ).filter(
                    CategoryDiscount.category_id == category_id,
                    CategoryDiscount.is_active == 1,
                    and_(
                        CategoryDiscount.starts_at <= current_time,
                        CategoryDiscount.ends_at >= current_time
                    )
                ).all()
                discount_list = [
                    {
                        'id': d.CategoryDiscount.id,
                        'category_id': d.CategoryDiscount.category_id,
                        'discount_percent': d.CategoryDiscount.discount_percent,
                        'starts_at': d.CategoryDiscount.starts_at,
                        'ends_at': d.CategoryDiscount.ends_at,
                        'is_active': d.CategoryDiscount.is_active,
                        'category_name': d.name
                    } for d in discounts
                ]
                logging.info(f"Retrieved {len(discount_list)} valid category discounts for category {category_id}")
                return discount_list
        except SQLAlchemyError as e:
            logging.error(f"Error retrieving valid category discounts for category {category_id}: {e}")
            return []

    def update_category_discount(self, discount_id, discount_percent=None, starts_at=None, ends_at=None, is_active=None):
        """Updates category discount details. Only provided fields are updated."""
        try:
            with next(self.get_db_session()) as session:
                discount = session.query(CategoryDiscount).filter_by(id=discount_id).first()
                if not discount:
                    logging.warning(f"No category discount found with ID: {discount_id}")
                    return False

                if discount_percent is not None:
                    discount.discount_percent = discount_percent
                if starts_at is not None:
                    discount.starts_at = starts_at
                if ends_at is not None:
                    discount.ends_at = ends_at
                if is_active is not None:
                    discount.is_active = is_active

                session.commit()
                logging.info(f"Updated category discount with ID: {discount_id}")
                return True
        except SQLAlchemyError as e:
            logging.error(f"Error updating category discount {discount_id}: {e}")
            return False

    def delete_category_discount(self, discount_id):
        """Deletes a category discount by its ID."""
        try:
            with next(self.get_db_session()) as session:
                discount = session.query(CategoryDiscount).filter_by(id=discount_id).first()
                if not discount:
                    logging.warning(f"No category discount found with ID: {discount_id}")
                    return False
                session.delete(discount)
                session.commit()
                logging.info(f"Deleted category discount with ID: {discount_id}")
                return True
        except SQLAlchemyError as e:
            logging.error(f"Error deleting category discount {discount_id}: {e}")
            return False

    def get_category_discounts(self, page=1, per_page=20):
        """Retrieves category discounts with pagination."""
        try:
            with next(self.get_db_session()) as session:
                total = session.query(CategoryDiscount).count()
                discounts = session.query(CategoryDiscount, Category.name).join(
                    Category, CategoryDiscount.category_id == Category.id
                ).order_by(CategoryDiscount.id).limit(per_page).offset((page - 1) * per_page).all()
                discount_list = [
                    {
                        'id': d.CategoryDiscount.id,
                        'category_id': d.CategoryDiscount.category_id,
                        'discount_percent': d.CategoryDiscount.discount_percent,
                        'starts_at': d.CategoryDiscount.starts_at,
                        'ends_at': d.CategoryDiscount.ends_at,
                        'is_active': d.CategoryDiscount.is_active,
                        'category_name': d.name
                    } for d in discounts
                ]
                logging.info(f"Retrieved {len(discount_list)} category discounts. Total: {total}")
                return discount_list, total
        except SQLAlchemyError as e:
            logging.error(f"Error retrieving category discounts: {e}")
            return [], 0

    def search_category_discounts(self, category_id=None, min_discount=None, max_discount=None, is_active=None, page=1, per_page=20):
        """Searches category discounts based on category_id, discount range, or is_active with pagination."""
        try:
            with next(self.get_db_session()) as session:
                query = session.query(CategoryDiscount, Category.name).join(
                    Category, CategoryDiscount.category_id == Category.id
                )
                if category_id is not None:
                    query = query.filter(CategoryDiscount.category_id == category_id)
                if min_discount is not None:
                    query = query.filter(CategoryDiscount.discount_percent >= min_discount)
                if max_discount is not None:
                    query = query.filter(CategoryDiscount.discount_percent <= max_discount)
                if is_active is not None:
                    query = query.filter(CategoryDiscount.is_active == is_active)

                total = query.count()
                discounts = query.order_by(CategoryDiscount.id).limit(per_page).offset((page - 1) * per_page).all()
                discount_list = [
                    {
                        'id': d.CategoryDiscount.id,
                        'category_id': d.CategoryDiscount.category_id,
                        'discount_percent': d.CategoryDiscount.discount_percent,
                        'starts_at': d.CategoryDiscount.starts_at,
                        'ends_at': d.CategoryDiscount.ends_at,
                        'is_active': d.CategoryDiscount.is_active,
                        'category_name': d.name
                    } for d in discounts
                ]
                logging.info(f"Found {len(discount_list)} category discounts matching search criteria. Total: {total}")
                return discount_list, total
        except SQLAlchemyError as e:
            logging.error(f"Error searching category discounts: {e}")
            return [], 0

    def delete_category_discounts_by_category(self, category_id):
        """Deletes all discounts for a specific category."""
        try:
            with next(self.get_db_session()) as session:
                deleted_count = session.query(CategoryDiscount).filter_by(category_id=category_id).delete()
                session.commit()
                logging.info(f"Deleted {deleted_count} category discounts for category {category_id}")
                return deleted_count
        except SQLAlchemyError as e:
            logging.error(f"Error deleting category discounts for category {category_id}: {e}")
            return 0

    def get_category_discount_stats(self):
        """Returns statistics about category discounts."""
        try:
            with next(self.get_db_session()) as session:
                total_discounts = session.query(CategoryDiscount).count()
                active_discounts = session.query(CategoryDiscount).filter(CategoryDiscount.is_active == 1).count()
                categories_with_discounts = session.query(func.count(func.distinct(CategoryDiscount.category_id))).scalar()
                average_discount = session.query(func.avg(CategoryDiscount.discount_percent)).scalar() or 0.0
                stats = {
                    'total_discounts': total_discounts,
                    'active_discounts': active_discounts,
                    'categories_with_discounts': categories_with_discounts,
                    'average_discount': round(float(average_discount), 2)
                }
                logging.info(f"Retrieved category discount stats: {stats}")
                return stats
        except SQLAlchemyError as e:
            logging.error(f"Error retrieving category discount stats: {e}")
            return {'total_discounts': 0, 'active_discounts': 0, 'categories_with_discounts': 0, 'average_discount': 0.0}

    def get_category_discount_stats_by_category(self, category_id):
        """Returns discount statistics for a specific category."""
        try:
            with next(self.get_db_session()) as session:
                total_discounts = session.query(CategoryDiscount).filter_by(category_id=category_id).count()
                active_discounts = session.query(CategoryDiscount).filter_by(category_id=category_id, is_active=1).count()
                average_discount = session.query(func.avg(CategoryDiscount.discount_percent)).filter_by(category_id=category_id).scalar() or 0.0
                stats = {
                    'total_discounts': total_discounts,
                    'active_discounts': active_discounts,
                    'average_discount': round(float(average_discount), 2)
                }
                logging.info(f"Retrieved discount stats for category {category_id}: {stats}")
                return stats
        except SQLAlchemyError as e:
            logging.error(f"Error retrieving discount stats for category {category_id}: {e}")
            return {'total_discounts': 0, 'active_discounts': 0, 'average_discount': 0.0}

    def toggle_category_discount_status(self, discount_id):
        """Toggles the is_active status of a category discount."""
        try:
            with next(self.get_db_session()) as session:
                discount = session.query(CategoryDiscount).filter_by(id=discount_id).first()
                if not discount:
                    logging.warning(f"No category discount found with ID: {discount_id}")
                    return False
                discount.is_active = 0 if discount.is_active == 1 else 1
                session.commit()
                logging.info(f"Toggled category discount status with ID: {discount_id} to is_active={discount.is_active}")
                return True
        except SQLAlchemyError as e:
            logging.error(f"Error toggling category discount status for ID {discount_id}: {e}")
            return False