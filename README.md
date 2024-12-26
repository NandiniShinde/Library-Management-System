# Library Management System

## Objective
This project implements a simple Library Management System (LMS) that allows users to perform basic operations such as adding books, borrowing books, returning books, and viewing available books.


- ## Features
    - **Add Books**: Allows users to add new books to the library with unique identifiers (ISBN), title, author, publication year, and total copies of the book avaliable.
    - **Borrow Books**: Users can borrow a book if it is available. The system ensures that the book is not already borrowed by the user and checks availability based on total copies.
    - **Return Books**: Users can return borrowed books, which updates the availability of the book and increases the total copies count by 1.
    - **View Available Books**: Displays a list of all available books in the library.


- ## Technologies Used
    - **Python**: Programming language used for backend development.
    - **Flask**: Web framework used to build the API.
    - **SQLAlchemy**: ORM used to interact with the database.
    - **Pytest**: Framework used to write and run tests.

- ## Setup

    - ### Prerequisites
        - Python 3.7 or higher
        - `pip` for installing dependencies

    - ### Installation
        - Clone this repository:
        ```bash
        git clone <https://github.com/NandiniShinde/Library-Management-System.git>
        ```
        - Install the required dependencies:
        ```bash
        pip install -r requirements.txt
        ```
        - Set up the database:
            - When you run the code, the database will be automatically created in your system. You do not need to download or set up any external database.
            - The project uses SQLAlchemy to manage database schema and interactions.
            - By default, an SQLite database (`library.db`) is created in the project directory when the application is first run.

        - Run the application:
        ```bash
        flask run
        ```

        The server will start at `http://127.0.0.1:5000/`.


- ## Endpoints
    - ### POST `/users`
        - **Description**: Adds a new user to the system.
        - **Body**:
        ```json
        {
            "name": "User Name",
            "email": "user@example.com"
        }
        ```

    - ### POST `/books`
        - **Description**: Adds a new book to the system.
        - **Body**:
        ```json
        {
            "isbn": "1234567890123",
            "title": "Book Title",
            "author": "Author Name",
            "publication_year": 2021,
            "total_copies": 5
        }
        ```

    - ### POST `/borrow`
        - **Description**: Allows a user to borrow a book.
        - **Body**:
        ```json
        {
            "isbn": "1234567890123",
            "user_id": 1
        }
        ```

    - ### POST `/return`
        - **Description**: Allows a user to return a borrowed book.
        - **Body**:
        ```json
        {
            "isbn": "1234567890123",
            "user_id": 1
        }
        ```

    - ### GET `/books?status=available`
        - **Description**: Returns a list of all available books in the library.


- ## Testing
    This project uses **pytest** for testing the functionality of the Library Management System. Tests have been written to ensure the following:
    - Correct addition of books
    - Borrowing and returning books
    - Availability of books after borrowing and returning

    - ### Run Tests
    To run the tests, use the following command:
    ```bash
    pytest
    ```

    The tests will ensure that all routes are functioning correctly and that the system updates the book counts and availability as expected.

- ## Git Usage and Version Control
Throughout the development process, Git was used to track changes, with frequent commits to ensure TDD principles were adhered to. The project is hosted in a Git repository and pushed to a remote server for version control.



- ## Test Report
The project includes comprehensive test coverage to validate the functionality of all features. The tests are written following TDD principles and ensure the correctness of critical operations like adding, borrowing, and returning books.

   - ### Generating the Test Report
    Open the test_report.html file in a browser to view the detailed results.
    Below is a summary of the test results:

   - ### Summary
    17 tests ran in 1.36 seconds.
    
    17 passed, 0 skipped, 0 failed, 0 errors, 0 expected failures, 0 unexpected passes
    For detailed results, refer to the attached test_report.html.

  - ### Generate the Test Coverage Report   
    To generate the test coverage report first install the pytest-cov for coverage reporting, and then run the following command in terminal.
    Command for installing - 
    ```bash
    pip install pytest-cov
    ```
    TO generate the report
    ```bash
    pytest --cov=app --cov-report=term --cov-report=html
    ```

   - ### Summary of the Coverage Report

    ----------- coverage: platform win32, python 3.7.3-final-0 -----------
    Name                Stmts   Miss  Cover
    ---------------------------------------
    app\__init__.py        12      0   100%
    app\extensions.py       2      0   100%
    app\models.py          56      4    93%
    app\routes.py          93      7    92%
    app\utils.py            7      0   100%
    ---------------------------------------
    TOTAL                 170     11    94%
    Coverage HTML written to dir htmlcov


- ## Conclusion
This project demonstrates the use of Test-Driven Development (TDD) principles to create a simple but functional Library Management System. It showcases basic operations like adding, borrowing, and returning books, with careful attention to maintaining accurate data regarding the availability of books.
    


