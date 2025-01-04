import pytest
import json
from app import create_app
from app.extensions import db
from app.models import Book
from app.utils import clear_books_db

@pytest.fixture
def client():
    """Sets up a test client for the Flask app and clears the database before each test.
    This ensures each test starts with a clean slate."""

    app = create_app()
    app.testing = True  # Enable testing mode
    
    # Clear the database before each test
    with app.app_context():
        clear_books_db()
    
     
    with app.test_client() as client:
        yield client

def test_home_route(client):
    """Tests if the home route responds with the expected welcome message.
    Ensures the application is correctly routing to the homepage."""

    # Send a GET request to the home route
    response = client.get('/')
    
    # Check if the status code is 200, else provide a descriptive message
    assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"
    
    # Check if the response data matches the expected output
    expected_message = "Welcome to the Library Management System!"
    actual_message = response.data.decode()
    assert actual_message == expected_message, f"Expected response data '{expected_message}', but got '{actual_message}'"

def test_add_book(client):
    """Validates the functionality to add a book to the library.
    Ensures that the book data is correctly stored and returned."""

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
    """Tests adding a book with missing required fields like ISBN or title.
    Ensures the system enforces mandatory fields and returns appropriate error messages."""

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
    """Tests adding a book with an invalid ISBN format.
    Ensures the ISBN validation logic correctly rejects invalid inputs."""

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
    """Tests adding a book with an ISBN that already exists in the library.
    Ensures the system prevents duplicate entries based on ISBN."""

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
    """Validates borrowing a book from the library.
    Ensures the book can be borrowed and the response confirms the action."""

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
    """Test borrowing a book that is already borrowed from the library by the same user."""

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

def test_borrow_book_with_single_available_copy(client):
    """Test borrowing a book when only one copy is available, and two users try to borrow it."""
    
    # Create a demo user
    user_payload = {
        "name": "Demo User",
        "email": "demo.user@example.com"
    }
    response = client.post('/users', json=user_payload)
    assert response.status_code == 201, "Failed to create user"

    # Create another user
    user_payload2 = {
        "name": "Another User",
        "email": "another.user@example.com"
    }
    response = client.post('/users', json=user_payload2)
    assert response.status_code == 201, "Failed to create another user"

    # Create a test book with 1 available copy
    book_payload = {
        "isbn": "1234567890123",
        "title": "Test Book with 1 Copy",
        "author": "Test Author",
        "publication_year": 2021,
        "total_copies": 1
    }
    response = client.post('/books', json=book_payload)
    assert response.status_code == 201, "Failed to add book"

    # Try borrowing the book for the first user (should succeed)
    borrow_payload = {
        "isbn": 1234567890123,
        "user_id": 1
    }
    response = client.post('/borrow', json=borrow_payload)
    assert response.status_code == 200, "Failed to borrow book for the first user"
    assert response.get_json()['message'] == "Book successfully borrowed."

    # Try borrowing the same book for the second user (should fail, no copies available)
    borrow_payload2 = {
        "isbn": 1234567890123,
        "user_id": 2
    }
    response = client.post('/borrow', json=borrow_payload2)
    assert response.status_code == 409, "Expected error when no copies are available"
    assert response.get_json()['message'] == "The book is not available."


def test_borrow_book_decreases_total_copies(client):
    """ Test to check if the count of total_copies is decreases on borrowing the book"""
    
    # Create a demo user
    user_payload = {
        "name": "Demo User",
        "email": "demo.user@example.com"
    }
    response = client.post('/users', json=user_payload)
    assert response.status_code == 201, "Failed to add user"
    
    # Add a book to the system with 1 copy
    book_payload = {
        "isbn": "1234567890123",
        "title": "Test Book",
        "author": "Test Author",
        "publication_year": 2021,
        "total_copies": 2
    }
    response = client.post('/books', json=book_payload)
    assert response.status_code == 201, "Failed to add book"
    
    # Borrow the book
    borrow_payload = {
        "isbn": "1234567890123",
        "user_id": 1  
    }
    response = client.post('/borrow', json=borrow_payload)
    assert response.status_code == 200, f"Failed to borrow the book: {response.json}"
    
    # Check that total_copies is increased by 1
    book = Book.query.filter_by(isbn="1234567890123").first()
    assert book.total_copies == 1, f"Expected 1 copies but got {book.total_copies}"


def test_borrow_book_and_make_it_unavailable(client):
    """Test to check the status of the book is changed to unavailable on borrowing the book"""
    
    # Create a demo user
    user_payload = {"name": "Demo User", "email": "demo.user@example.com"}
    response = client.post('/users', json=user_payload)
    assert response.status_code == 201, "Failed to add user"
    
    # Add a book to the system with 1 copy
    book_payload = {
        "isbn": "1234567890123",
        "title": "Test Book",
        "author": "Test Author",
        "publication_year": 2021,
        "total_copies": 1
    }
    response = client.post('/books', json=book_payload)
    assert response.status_code == 201, "Failed to add book"
    
    # Borrow the book, which will make it unavailable
    borrow_payload = {
        "isbn": "1234567890123",
        "user_id": 1  
    }
    response = client.post('/borrow', json=borrow_payload)
    assert response.status_code == 200, f"Failed to borrow the book: {response.json}"
    
    # Check that the status is now 'unavailable'
    book = Book.query.filter_by(isbn="1234567890123").first()
    assert book.status == "unavailable", f"Expected 'unavailable' but got {book.status}"


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

def test_case_view_available_books(client):
    """Test viewing only the books that are currently available in the library."""

    # Add some books to the system
    books_payload = {
            "isbn": "1111111111111",
            "title": "Available Book 1",
            "author": "Author 1",
            "publication_year": 2010,
        }
    response = client.post('/books', json=books_payload)
    assert response.status_code == 201, f"Failed to add book: {books_payload['title']}"
    
    books_payload =     {
            "isbn": "2222222222222",
            "title": "Available Book 2",
            "author": "Author 2",
            "publication_year": 2015
        }
    response = client.post('/books', json=books_payload)
    assert response.status_code == 201, f"Failed to add book: {books_payload['title']}"
    
    books_payload = {
            "isbn": "3333333333333",
            "title": "Borrowed Book",
            "author": "Author 3",
            "publication_year": 2020
        }
    response = client.post('/books', json=books_payload)
    assert response.status_code == 201, f"Failed to add book: {books_payload['title']}"


    # Create a demo user 
    user_payload = {
        "name": "Demo User",
        "email": "demo.user@example.com"
    }

    # Add user to the database (via POST /users route)
    response = client.post('/users', json=user_payload)

    # Borrow the third book to make it unavailable
    borrow_payload = {
        "isbn": "3333333333333",  # ISBN of the book to borrow
        "user_id": 1  # Assuming a valid user ID exists
    }
    response = client.post('/borrow', json=borrow_payload)
    assert response.status_code == 200, "Failed to borrow the book"

    # Fetch available books
    response = client.get('/books?status=available')
    assert response.status_code == 200, "Failed to fetch available books"

    # Validate the response
    available_books = response.json
    assert len(available_books) == 2, "Incorrect number of available books returned"
    assert all(book["isbn"] in ["1111111111111", "2222222222222"] for book in available_books), "Returned books do not match expected available books"
    
def test_return_book_increases_total_copies(client):
    """Test that returning a book increases the total copies by 1."""
    
    # Create a demo user
    user_payload = {"name": "Demo User", "email": "demo.user@example.com"}
    response = client.post('/users', json=user_payload)
    assert response.status_code == 201, "Failed to add user"
    
    # Add a book to the system with 1 copy
    book_payload = {
        "isbn": "1234567890123",
        "title": "Test Book",
        "author": "Test Author",
        "publication_year": 2021,
        "total_copies": 2
    }
    response = client.post('/books', json=book_payload)
    assert response.status_code == 201, "Failed to add book"
    
    # Borrow the book
    borrow_payload = {
        "isbn": "1234567890123",
        "user_id": 1  
    }
    response = client.post('/borrow', json=borrow_payload)
    assert response.status_code == 200, f"Failed to borrow the book: {response.json}"
    
    # Return the book
    return_payload = {
        "isbn": "1234567890123",
        "user_id": 1  
    }
    response = client.post('/return', json=return_payload)
    assert response.status_code == 200, f"Failed to return the book: {response.json}"
    
    # Check that total_copies is increased by 1
    book = Book.query.filter_by(isbn="1234567890123").first()
    assert book.total_copies == 2, f"Expected 2 copies but got {book.total_copies}"

def test_return_unavailable_book_and_make_it_available(client):
    """Test that returning an unavailable book changes its status to available."""
    
    # Create a demo user
    user_payload = {"name": "Demo User", "email": "demo.user@example.com"}
    response = client.post('/users', json=user_payload)
    assert response.status_code == 201, "Failed to add user"
    
    # Add a book to the system with 1 copy
    book_payload = {
        "isbn": "1234567890123",
        "title": "Test Book",
        "author": "Test Author",
        "publication_year": 2021,
        "total_copies": 1
    }
    response = client.post('/books', json=book_payload)
    assert response.status_code == 201, "Failed to add book"
    
    # Borrow the book, which will make it unavailable
    borrow_payload = {
        "isbn": "1234567890123",
        "user_id": 1  # Assuming user ID 1 exists
    }
    response = client.post('/borrow', json=borrow_payload)
    assert response.status_code == 200, f"Failed to borrow the book: {response.json}"
    
    # Return the book and check its status
    return_payload = {
        "isbn": "1234567890123",
        "user_id": 1  # Assuming user ID 1 exists
    }
    response = client.post('/return', json=return_payload)
    assert response.status_code == 200, f"Failed to return the book: {response.json}"
    
    # Check that the status is now 'available'
    book = Book.query.filter_by(isbn="1234567890123").first()
    assert book.status == "available", f"Expected 'available' but got {book.status}"
    
    # Check if the book is now visible in available books (status = 'available')
    response = client.get('/books?status=available')
    available_books = response.json
    assert any(b['isbn'] == "1234567890123" for b in available_books), "Returned book should be available"


def test_return_unavailable_book(client):
    """Test that returning an unavailable book changes its status to available."""
    
    # Add a book to the system with 0 copy
    book_payload = {
        "isbn": "1234567890123",
        "title": "Test Book",
        "author": "Test Author",
        "publication_year": 2021,
        "total_copies": 0,
        "status": "unavailable"
    }
    response = client.post('/books', json=book_payload)
    assert response.status_code == 201, "Failed to add book"

    book_payload = {
        "isbn": "4815897463248",
        "title": "Test Book 2",
        "author": "Test Author 2",
        "publication_year": 2021,
        "total_copies": 0,
        "status": "unavailable"
    }
    response = client.post('/books', json=book_payload)
    assert response.status_code == 201, "Failed to add book"

    # Check if the book is now visible in unavailable books (status = 'unavailable')
    response = client.get('/books?status=unavailable')
    unavailable_books = response.json
    assert any(b['isbn'] == "1234567890123" for b in unavailable_books), "Returned all unavailable books"


def test_all_book_borrowed_by_a_user(client):
    """Test that returns all the books borrowed by the user."""

    # Create a demo user
    user_payload = {"name": "Demo User", "email": "demo.user@example.com"}
    response = client.post('/users', json=user_payload)
    assert response.status_code == 201, "Failed to add user"

    # Add a book to the system with 1 copy
    book_payload = {
        "isbn": "1234567890123",
        "title": "Test Book",
        "author": "Test Author",
        "publication_year": 2021,
        "total_copies": 1
    }
    response = client.post('/books', json=book_payload)
    assert response.status_code == 201, "Failed to add book"

    book_payload = {
        "isbn": "1234567756123",
        "title": "Test Book 2",
        "author": "Test Author 2",
        "publication_year": 2021,
        "total_copies": 1
    }
    response = client.post('/books', json=book_payload)
    assert response.status_code == 201, "Failed to add book"
    
    # Borrow the book, which will make it unavailable
    borrow_payload = {
        "isbn": "1234567890123",
        "user_id": 1  
    }
    response = client.post('/borrow', json=borrow_payload)
    assert response.status_code == 200, f"Failed to borrow the book: {response.json}"

    borrow_payload = {
        "isbn": "1234567756123",
        "user_id": 1  
    }
    response = client.post('/borrow', json=borrow_payload)
    assert response.status_code == 200, f"Failed to borrow the book: {response.json}"

    # borrowed_books = ['1234567890123','1234567756123']

    # Fetch all books borrowed by the user
    response = client.get(f'/users/1/borrowed-books')
    assert response.status_code == 200, "Failed to fetch borrowed books"

    print("Test passed: Borrowed books fetched successfully.")

def test_total_borrowed_book_by_user(client):
    # Create a demo user
    user_payload = {"name": "Demo User", "email": "demo.user@example.com"}
    response = client.post('/users', json=user_payload)
    assert response.status_code == 201, "Failed to add user"

    # Add a book to the system with 1 copy
    book_payload = {
        "isbn": "1234567890123",
        "title": "Test Book",
        "author": "Test Author",
        "publication_year": 2021,
        "total_copies": 1
    }
    response = client.post('/books', json=book_payload)
    assert response.status_code == 201, "Failed to add book"

    book_payload = {
        "isbn": "1234567756123",
        "title": "Test Book 2",
        "author": "Test Author 2",
        "publication_year": 2021,
        "total_copies": 1
    }
    response = client.post('/books', json=book_payload)
    assert response.status_code == 201, "Failed to add book"

    book_payload = {
        "isbn": "1234567966123",
        "title": "Harry Potter 3",
        "author": "Nandini 3",
        "publication_year": 2021,
        "total_copies": 1
    }
    response = client.post('/books', json=book_payload)
    assert response.status_code == 201, "Failed to add book"
    
    # Borrow the book, which will make it unavailable
    borrow_payload = {
        "isbn": "1234567890123",
        "user_id": 1  
    }
    response = client.post('/borrow', json=borrow_payload)
    assert response.status_code == 200, f"Failed to borrow the book: {response.json}"

    borrow_payload = {
        "isbn": "1234567756123",
        "user_id": 1  
    }
    response = client.post('/borrow', json=borrow_payload)
    assert response.status_code == 200, f"Failed to borrow the book: {response.json}"

    borrow_payload = {
        "isbn": "1234567966123",
        "user_id": 1  
    }
    response = client.post('/borrow', json=borrow_payload)
    assert response.status_code == 400, f"User is able to borrow more than two books: {response.json}"

