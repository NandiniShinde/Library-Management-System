import pytest
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
