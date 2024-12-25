from flask import Flask,  request, jsonify
from app.models import Book
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
            publication_year=data['publication_year']
        )

        db.session.add(new_book)
        db.session.commit()

        return jsonify(new_book.to_dict()), 201
