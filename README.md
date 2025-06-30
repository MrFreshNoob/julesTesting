# Online Video Game Store

A Flask-based web application simulating an online video game store.

## Features (Planned & In-Progress)

*   User registration and login
*   Game store page displaying available games
*   Game library for owned games
*   Shopping cart and (simulated) purchase functionality
*   Friend system (add by gamertag or friend code)

## Setup and Running

1.  **Clone the repository (if applicable).**

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up the Flask application environment variables:**
    ```bash
    export FLASK_APP=app.py  # On Windows: set FLASK_APP=app.py
    # For development, you can also enable debug mode (optional)
    # export FLASK_ENV=development # On Windows: set FLASK_ENV=development
    ```
    *Note: If `FLASK_ENV` is set to `development`, the server will automatically reload on code changes and provide a debugger.*

5.  **Initialize the database:**
    Run the following command *once* to create the database schema and add initial game data:
    ```bash
    flask init-db
    ```
    This will create a `game_store.db` file in the project root.

6.  **Run the Flask development server:**
    ```bash
    flask run
    ```
    The application should be accessible at `http://127.0.0.1:5000/`.

## Project Structure

*   `app.py`: Main Flask application file containing routes and logic.
*   `database_setup.py`: Script to initialize the SQLite database and schema.
*   `game_store.db`: SQLite database file (created after running `flask init-db`).
*   `requirements.txt`: Python package dependencies.
*   `static/`: Contains static files (CSS, JavaScript, images).
    *   `style.css`: Basic stylesheet.
    *   `images/`: Placeholder for game images.
*   `templates/`: Contains HTML templates.
    *   `base.html`: Base template for common layout.
    *   `index.html`: Store page.
    *   `login.html`: User login page.
    *   `register.html`: User registration page.
    *   `library.html`: User's game library.
    *   `friends.html`: Friends management page.

## Next Steps / TODO

*   Implement "Add to Cart" and "Buy Now" logic.
*   Complete friend request sending/acceptance/rejection logic.
*   Flesh out the game details page.
*   Add more robust error handling and user feedback.
*   Implement pagination for game listings and friend lists if they grow large.
*   Add actual game images to `static/images/` and update `database_setup.py`.
*   Write unit and integration tests.
*   Improve styling and user interface.
```
