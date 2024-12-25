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


def test_case_borrow_book_not_found(client):
    """Test borrowing a book that doesn't exist in the library."""

    # Create a demo user 
    user_payload = {
        "name": "Demo User",
        "email": "demo.user@example.com"
    }

    # Add user to the database (via POST /users route)
    response = client.post('/users', json=user_payload)
    
    # Try to borrow a book with a non-existent ISBN
    borrow_payload = {
        "isbn": "9999999999999",  # ISBN that does not exist in the system
        "user_id": 1  # Assuming user ID 1 exists
    }

    response = client.post('/borrow', json=borrow_payload)

    # Check the status code and ensure it indicates a "not found" error (404)
    assert response.status_code == 404, f"Expected 404 but got {response.status_code}"

    # Check the response message to verify it indicates the book doesn't exist
    assert response.json.get("message") == "Book not found", f"Unexpected message: {response.json.get('message')}"


def test_case_borrow_book_already_borrowed(client):
    """Test borrowing a book that is already borrowed from the library."""

    # Create a demo user 
    user_payload = {
        "name": "Demo User",
        "email": "demo.user@example.com"
    }

    # Add user to the database (via POST /users route)
    response = client.post('/users', json=user_payload)
       

    # Create and add a book to the system
    book_payload = {
        "isbn": "1234567890123",
        "title": "Test Book",
        "author": "Test Author",
        "publication_year": 2021
    }
    
    response = client.post('/books', json=book_payload)
    assert response.status_code == 201, "Failed to add the book"

    # Mark the book as borrowed manually 
    borrow_payload = {
        "isbn": "1234567890123",
        "user_id": 1  # Assuming user ID 1 exists
    }
    client.post('/borrow', json=borrow_payload)
    
    # Now try to borrow the same book again
    borrow_again_payload = {
        "isbn": "1234567890123",  # ISBN of the book that is already borrowed by the user
        "user_id": 1  
    }

    response = client.post('/borrow', json=borrow_again_payload)

    # Check the status code to ensure it was a "conflict" error (409)
    assert response.status_code == 409, f"Expected 409 but got {response.status_code}"

    # Check the response message to verify it indicates the book is already borrowed
    assert response.json.get("message") == "Book is already borrowed by user.", f"Unexpected message: {response.json.get('message')}"


def test_case_return_book(client):
    """Test the ability to return a borrowed book to the library."""
    
    # Create a demo user 
    user_payload = {
        "name": "Demo User",
        "email": "demo.user@example.com"
    }
    response = client.post('/users', json=user_payload)
    assert response.status_code == 201, f"Failed to create user: {response.json.get('message')}"

    # Create and add a book to the system
    book_payload = {
        "isbn": "1234567890123",
        "title": "Test Book",
        "author": "Test Author",
        "publication_year": 2021
    }
    response = client.post('/books', json=book_payload)
    assert response.status_code == 201, "Failed to add the book"

    # Borrow the book
    borrow_payload = {
        "isbn": "1234567890123",  # ISBN of the book to borrow
        "user_id": 1  
    }
    response = client.post('/borrow', json=borrow_payload)
    assert response.status_code == 200, "Failed to borrow the book"
    assert response.json.get("message") == "Book successfully borrowed."

    # Now return the book
    return_payload = {
        "isbn": "1234567890123",  # ISBN of the book to return
        "user_id": 1  # User ID 1 is returning the book
    }

    response = client.post('/return', json=return_payload)

    # Check the status code and ensure it was successful (200 OK)
    assert response.status_code == 200, "Failed to return the book"

    # Check the response message to verify the book was returned successfully
    assert response.json.get("message") == "Book successfully returned."


def test_case_return_not_borrowed_book(client):
    """Test attempting to return a book that is not currently borrowed."""

    # Create a test book that is available
    payload = {
        "isbn": "9999999999999",
        "title": "Available Book",
        "author": "Author Example",
        "publication_year": 2020
    }

    # Add the book to the database
    response = client.post('/books', json=payload)
    assert response.status_code == 201, "Failed to add the book"
    
    # Create a demo user 
    user_payload = {
        "name": "Demo User",
        "email": "demo.user@example.com"
    }

    # Add user to the database (via POST /users route)
    response = client.post('/users', json=user_payload)
       

    # Try to return the book (which is not borrowed)
    return_payload = {
        "isbn": "9999999999999",  # The ISBN of the book
        "user_id": 1  # Assuming a valid user ID exists
    }

    response = client.post('/return', json=return_payload)

    # Ensure the status code and error message are correct
    assert response.status_code == 400, "Expected failure for returning a book not borrowed"
    assert response.json.get("message") == "Book is not currently borrowed."


def test_case_return_nonexistent_book(client):
    """Test attempting to return a book that doesn't exist in the system."""

    # Attempt to return a nonexistent book
    return_payload = {
        "isbn": "0000000000000",  # Nonexistent ISBN
        "user_id": 1  # Assuming a valid user ID exists
    }

    response = client.post('/return', json=return_payload)

    # Ensure the status code and error message are correct
    assert response.status_code == 404, "Expected failure for returning a nonexistent book"
    assert response.json.get("message") == "Book not found."
