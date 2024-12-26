from flask import Flask,  request, jsonify
from sqlalchemy import func
from app.models import Book, BorrowedBooks, User
from app.extensions import db

def configure_routes(app: Flask):
    @app.route('/', methods=['GET'])
    def home():
        return "Welcome to the Library Management System!"
    
    @app.route('/books', methods=['POST'])
    def add_book():
        data = request.get_json()

        # Validate input data
        isbn = data.get("isbn")
        title = data.get("title")
        author = data.get("author")
        publication_year = data.get("publication_year")
        
        # Default status to 'available' if not provided
        status = data.get('status', 'available')

        # Validate ISBN
        valid_isbn, isbn_message = Book.validate_isbn(isbn)
        if not valid_isbn:
            return jsonify({"error": isbn_message}), 400

        # Validate title
        valid_title, title_message = Book.validate_title(title)
        if not valid_title:
            return jsonify({"error": title_message}), 400

        # Validate publication year
        valid_year, year_message = Book.validate_publication_year(publication_year)
        if not valid_year:
            return jsonify({"error": year_message}), 400
        
        # Check if the book already exists
        existing_book = Book.query.filter_by(isbn=data['isbn']).first()
        if existing_book:
            return jsonify({"error": "Book with this ISBN already exists"}), 409

        # Create a new book
        new_book = Book(
            isbn=data['isbn'],
            title=data['title'],
            author=data['author'],
            publication_year=data['publication_year'],
            total_copies=data.get('total_copies', 1),  # Default to 1 if not provided
            status=status  # Set the status field
        )

        db.session.add(new_book)
        db.session.commit()

        return jsonify(new_book.to_dict()), 201



    @app.route('/users', methods=['POST'])
    def add_user():
        """Add a new user to the system."""
        data = request.get_json()
        
        # Validate input data
        if not data or 'name' not in data or 'email' not in data:
            return jsonify({"message": "Name and email are required fields"}), 400
        
        name = data['name']
        email = data['email']
        
        # Check if user with the same email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({"message": "User with this email already exists"}), 409
        
        # Create a new user
        new_user = User(name=name, email=email)
        
        # Add the new user to the database
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify(new_user.to_dict()), 201


    @app.route('/borrow', methods=['POST'])
    def borrow_book():
        """Allow a user to borrow a book."""
        data = request.get_json()
        
        # Check if the user exists
        user = User.query.filter_by(id=data.get('user_id')).first()
        if not user:
            return jsonify({"message": "User not found"}), 404
        
        # Check if the book exists
        book = Book.query.filter_by(isbn=data.get('isbn')).first()
        if not book:
            return jsonify({"message": "Book not found"}), 404

        # Check if the book is already borrowed by the user
        if book in user.borrowed_books:
            return jsonify({"message": "Book is already borrowed by user."}), 409
        
        # Check if the book is available (total_copies - borrowed_count > 0)
        borrowed_count = db.session.query(BorrowedBooks).filter_by(book_id=book.id).count()
        if borrowed_count >= book.total_copies:
            # If no copies are available, set the status to 'unavailable'
            book.status = "unavailable"
            db.session.commit()
            return jsonify({"message": "The book is not available."}), 409  # Conflict: book is not available

        # Add the book to the user's borrowed books
        user.borrowed_books.append(book)

        # Decrement the total copies by 1
        book.total_copies -= 1
        
        # If the total copies are 0, set the status to 'unavailable'
        if book.total_copies == 0:
            book.status = "unavailable"

        # Commit the transaction to save the changes
        db.session.commit()
        
        return jsonify({"message": "Book successfully borrowed."}), 200


    @app.route('/return', methods=['POST'])
    def return_book():
        """Handle returning a borrowed book."""
        
        # Parse incoming JSON data
        data = request.get_json()
        isbn = data.get('isbn')
        user_id = data.get('user_id')

        # Check if the book exists
        book = Book.query.filter_by(isbn=isbn).first()
        if not book:
            return jsonify({"message": "Book not found."}), 404

        # Check if the user exists
        user = db.session.get(User, user_id)
        if not user:
            return jsonify({"message": "User not found."}), 404

        # Check if the book was borrowed by the user
        borrowed_book = BorrowedBooks.query.filter_by(book_id=book.id, user_id=user.id).first()
        if not borrowed_book:
            return jsonify({"message": "Book is not currently borrowed."}), 400
        
        # Remove the record from the BorrowedBooks table
        db.session.delete(borrowed_book)
        
        # Increment the total_copies of the book when it is returned
        print(f"Before return, total copies: {book.total_copies}")
        book.total_copies += 1
        print(f"After return, total copies: {book.total_copies}")

        
        # If the book was previously unavailable, set its status back to available
        if book.status == "unavailable":
            book.status = "available"
        
        # Commit the changes to the database
        db.session.commit()

        # Return a success message
        return jsonify({"message": "Book successfully returned."}), 200

    
    @app.route('/books', methods=['GET'])
    def view_avaiable_books():
        """
        View books in the library.
        If `status=available` is provided as a query parameter, return only available books.
        Otherwise, return all books.
        """
        status = request.args.get('status')

        if status == "available":
            # Query to find books where borrowed copies are less than total copies
            available_books = (
                db.session.query(Book)
                .outerjoin(BorrowedBooks, Book.id == BorrowedBooks.book_id)
                .group_by(Book.id)
                .having(func.count(BorrowedBooks.book_id) < Book.total_copies)
                .all() 
            )
            books_data = [book.to_dict() for book in available_books]
        else:
            # Return all books without filtering
            books = Book.query.all()
            books_data = [book.to_dict() for book in books]

        return jsonify(books_data), 200