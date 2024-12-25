import pytest
import json
from app import create_app
from app.extensions import db
from app.models import Book
from app.utils import clear_books_db

@pytest.fixture
def client():
    app = create_app()
    app.testing = True  # Enable testing mode
     
    # Clear the database before each test
    with app.app_context():
        clear_books_db()

    with app.test_client() as client:
        yield client

def test_home_route(client):
    """Test that the home route returns the correct response."""
    
    # Send a GET request to the home route
    response = client.get('/')
    
    # Check if the status code is 200, else provide a descriptive message
    assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"
    
    # Check if the response data matches the expected output
    expected_message = "Welcome to the Library Management System!"
    actual_message = response.data.decode()
    assert actual_message == expected_message, f"Expected response data '{expected_message}', but got '{actual_message}'"

def test_add_book(client):
    """Test the ability to add a book to the library."""
    payload = {
        "isbn": "1234567897532",
        "title": "First Book",
        "author": "Nandini Shinde",
        "publication_year": 2020
    }
    response = client.post('/books', json=payload)
    assert response.status_code == 201, "Failed to create a book"
    response_data = response.get_json()
    assert response_data["isbn"] == "1234567897532", "The ISBN should match"
    assert response_data["title"] == "First Book", "The title should match"
    assert response_data["author"] == "Nandini Shinde", "The author should match"
    assert response_data["publication_year"] == 2020, "The year should match"

def test_add_book_missing_fields(client):
    """Test adding a book with missing required fields."""
    # Missing 'isbn'
    payload = {
        "title": "Second Book",
        "author": "John Doe",
        "publication_year": 2021
    }
    response = client.post('/books', json=payload)
    assert response.status_code == 400, f"Expected 400, got {response.status_code}"
    assert b"ISBN must not be empty." in response.data

    # Missing 'title'
    payload = {
        "isbn": "1234567890159",
        "author": "Jane Doe",
        "publication_year": 2021
    }
    response = client.post('/books', json=payload)
    assert response.status_code == 400, f"Expected 400, got {response.status_code}"
    assert b"Title must not be empty." in response.data

def test_add_book_invalid_isbn(client):
    """Test adding a book with an invalid ISBN format."""
    payload = {
        "isbn": "INVALID_ISBN",
        "title": "Third Book",
        "author": "Alice Smith",
        "publication_year": 2022
    }
    response = client.post('/books', json=payload)
    assert response.status_code == 400, f"Expected 400, got {response.status_code}"
    assert b"ISBN must be 13 characters long." in response.data

  
def test_add_book_duplicate_isbn(client):
    """Test adding a duplicate book (same ISBN)."""
    # First, add the book
    payload = {
        "isbn": "1234567891234",
        "title": "Fourth Book",
        "author": "Bob Lee",
        "publication_year": 2023
    }
    response = client.post('/books', json=payload)
    
    # Try to add the same book again (should conflict)
    response = client.post('/books', json=payload)
    assert response.status_code == 409, f"Expected 409, got {response.status_code}"
    assert b"Book with this ISBN already exists" in response.data


def test_case_borrow_book(client):
    """Test the ability to borrow a book from the library."""

     # Create a demo user 
    user_payload = {
        "name": "Demo User",
        "email": "demo.user@example.com"
    }

    # Add user to the database (via POST /users route)
    response = client.post('/users', json=user_payload)

    # Create a test book 
    payload = {
        "isbn": "1234567890123",
        "title": "Test Book",
        "author": "Test Author",
        "publication_year": 2021
    }

    # Add the book to the database (via POST /books route)
    response = client.post('/books', json=payload)
    assert response.status_code == 201, "Failed to add the book"

    # Now try to borrow the book
    borrow_payload = {
        "isbn": "1234567890123",  # ISBN of the book to borrow
        "user_id": 1  
    }

    response = client.post('/borrow', json=borrow_payload)

    # Check the status code to ensure it was successful
    assert response.status_code == 200, "Failed to borrow the book"
    
    # Check the response message 
    assert response.json.get("message") == "Book successfully borrowed."