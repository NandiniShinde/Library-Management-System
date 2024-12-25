from app.extensions import db

class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    isbn = db.Column(db.String(13), unique=True, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    publication_year = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(50), default="available", nullable=False)
    total_copies = db.Column(db.Integer, nullable=False, default=1)

    borrowers = db.relationship('User', secondary='borrowed_books', backref='borrowed_books')

    def __init__(self, isbn, title, author, publication_year, status, total_copies):
        self.isbn = isbn
        self.title = title
        self.author = author
        self.publication_year = publication_year
        self.status = status
        self.total_copies = total_copies

    def to_dict(self):
        """Convert Book instance to dictionary."""
        return {
            "id": self.id,
            "isbn": self.isbn,
            "title": self.title,
            "author": self.author,
            "publication_year": self.publication_year,
            "status": self.status,
            "total_copies": self.total_copies
        }

    @staticmethod
    def validate_isbn(isbn):
        if isbn is None:
            return False, "ISBN must not be empty."
        if len(isbn) != 13:
            return False, "ISBN must be 13 characters long."
        return True, ""

    @staticmethod
    def validate_title(title):
        if title is None:
            return False, "Title must not be empty."
        if not title:
            return False, "Title must not be empty."
        if len(title) > 255:
            return False, "Title is too long."
        return True, ""
    
    @staticmethod
    def validate_publication_year(publication_year):
        if publication_year is None:
            return False, "Publication year must not be empty."
        if not isinstance(publication_year, int) or publication_year < 1000 or publication_year > 2100:
            return False, "Publication year must be a valid number between 1000 and 2100."
        return True, ""
    

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)

    
    

    def __init__(self, name, email):
        self.name = name
        self.email = email

    def to_dict(self):
        """Convert User instance to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email
        }

class BorrowedBooks(db.Model):
    """Intermediate table to track borrowed books."""
    __tablename__ = 'borrowed_books'
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), primary_key=True)
    borrowed_at = db.Column(db.DateTime, default=db.func.now())
    return_by = db.Column(db.DateTime)

    