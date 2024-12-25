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

        if not data or 'isbn' not in data or 'title' not in data or 'author' not in data or 'publication_year' not in data:
            return jsonify({"error": "Invalid data"}), 400

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
