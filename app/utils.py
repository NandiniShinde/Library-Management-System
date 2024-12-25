from app.extensions import db
from app.models import Book

def clear_books_db():
    """Delete all records from the Book table."""
    db.session.query(Book).delete()
    db.session.commit()
