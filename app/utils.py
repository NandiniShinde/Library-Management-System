from app.extensions import db
from app.models import Book, User, BorrowedBooks

def clear_books_db():
    """Delete all records from the Book table."""
    db.session.query(Book).delete()
    db.session.query(User).delete()
    db.session.query(BorrowedBooks).delete()
    db.session.commit()
