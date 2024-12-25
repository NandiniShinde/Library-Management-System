import pytest
import json
from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.testing = True  # Enable testing mode
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
        "isbn": "1234567890",
        "title": "Sample Book",
        "author": "John Doe",
        "year": 2020
    }
    response = client.post('/books', json=payload)
    assert response.status_code == 201, "Failed to create a book"
    response_data = response.get_json()
    assert response_data["id"] == 1, "The book ID should be 1"
    assert response_data["isbn"] == "1234567890", "The ISBN should match"
    assert response_data["title"] == "Sample Book", "The title should match"
    assert response_data["author"] == "John Doe", "The author should match"
    assert response_data["year"] == 2020, "The year should match"