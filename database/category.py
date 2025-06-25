from .base import Database, Category
from sqlalchemy import select, func
import logging

class CategoryManager(Database):
    """Manages operations for the categories table in the database using SQLAlchemy ORM."""

    def add_category(self, name, parent_id=None, image_url=""):
        """Adds a new category."""
        try:
            with next(self.get_db_session()) as session:
                # Validate required fields
                if not name:
                    logging.error("Category name is required")
                    return None

                # Create new category
                new_category = Category(
                    name=name,
                    parent_id=parent_id,
                    image_url=image_url
                )
                session.add(new_category)
                session.commit()
                category_id = new_category.id
                logging.info(f"Category {name} added with ID: {category_id}")
                return category_id
        except Exception as e:
            logging.error(f"Error adding category {name}: {e}")
            return None

    def get_category_by_id(self, category_id):
        """Retrieves a category by its ID."""
        try:
            with next(self.get_db_session()) as session:
                category = session.get(Category, category_id)
                if category:
                    logging.info(f"Retrieved category with ID: {category_id}")
                    return category
                else:
                    logging.warning(f"No category found with ID: {category_id}")
                    return None
        except Exception as e:
            logging.error(f"Error retrieving category by ID {category_id}: {e}")
            return None

    def get_categories_by_parent(self, parent_id=None):
        """Retrieves all categories with the specified parent_id (or top-level if None)."""
        try:
            with next(self.get_db_session()) as session:
                query = select(Category).where(Category.parent_id == parent_id if parent_id is not None else Category.parent_id.is_(None))
                categories = session.execute(query).scalars().all()
                logging.info(f"Retrieved {len(categories)} categories with parent_id: {parent_id}")
                return categories
        except Exception as e:
            logging.error(f"Error retrieving categories with parent_id {parent_id}: {e}")
            return []

    def update_category(self, category_id, name=None, parent_id=None, image_url=None):
        """Updates category details. Only provided fields are updated."""
        try:
            with next(self.get_db_session()) as session:
                category = session.get(Category, category_id)
                if not category:
                    logging.warning(f"No category found with ID: {category_id}")
                    return False

                if name is not None:
                    category.name = name
                if parent_id is not None:
                    category.parent_id = parent_id
                if image_url is not None:
                    category.image_url = image_url

                session.commit()
                logging.info(f"Updated category with ID: {category_id}")
                return True
        except Exception as e:
            logging.error(f"Error updating category {category_id}: {e}")
            return False

    def delete_category(self, category_id):
        """Deletes a category by its ID."""
        try:
            with next(self.get_db_session()) as session:
                category = session.get(Category, category_id)
                if not category:
                    logging.warning(f"No category found with ID: {category_id}")
                    return False

                session.delete(category)
                session.commit()
                logging.info(f"Deleted category with ID: {category_id}")
                return True
        except Exception as e:
            logging.error(f"Error deleting category {category_id}: {e}")
            return False

    def get_categories(self, page=1, per_page=20):
        """Retrieves categories with pagination."""
        try:
            with next(self.get_db_session()) as session:
                # Get total count
                total_query = select(func.count()).select_from(Category)
                total = session.execute(total_query).scalar()

                # Get paginated categories
                query = select(Category).order_by(Category.name).limit(per_page).offset((page - 1) * per_page)
                categories = session.execute(query).scalars().all()
                logging.info(f"Retrieved {len(categories)} categories. Total: {total}")
                return categories, total
        except Exception as e:
            logging.error(f"Error retrieving categories: {e}")
            return [], 0

    def search_categories(self, search_term, page=1, per_page=20):
        """Searches categories by name with pagination."""
        try:
            with next(self.get_db_session()) as session:
                # Build search query
                search_pattern = f"%{search_term}%"
                query = select(Category).where(Category.name.ilike(search_pattern))
                
                # Get total count
                total_query = select(func.count()).select_from(Category).where(Category.name.ilike(search_pattern))
                total = session.execute(total_query).scalar()

                # Get paginated results
                query = query.order_by(Category.name).limit(per_page).offset((page - 1) * per_page)
                categories = session.execute(query).scalars().all()
                logging.info(f"Retrieved {len(categories)} categories for search term '{search_term}'. Total: {total}")
                return categories, total
        except Exception as e:
            logging.error(f"Error searching categories with term '{search_term}': {e}")
            return [], 0