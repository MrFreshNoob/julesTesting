# Online Video Game Store

A Flask-based web application simulating an online video game store.

## Prerequisites for Running (Especially on Windows)

*   **Python:** You need Python installed. Version 3.7+ is recommended.
    *   **Download Python:** [https://www.python.org/downloads/](https://www.python.org/downloads/)
    *   **IMPORTANT for Windows:** During installation, make sure to check the box that says **"Add Python to PATH"** or **"Add python.exe to PATH"**. If you've already installed Python, you might need to reinstall it or manually add Python to your PATH environment variable.
*   **Pip:** Pip is the Python package installer. It usually comes with Python if you install a recent version.
*   **Git (Optional, for cloning):** If you haven't downloaded the code as a ZIP.

**How to check if Python and Pip are installed and in PATH:**
Open a Command Prompt (search `cmd`) or PowerShell and type:
```bash
python --version
pip --version
```
If you see version numbers, they are likely installed and in your PATH. If you get a "command not found" error, they are not correctly set up in your PATH.

## Setup and Running Instructions

1.  **Clone the repository or download the source code.**
    If you have Git:
    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```
    If you downloaded a ZIP, extract it and navigate into the project's root directory in your terminal.

2.  **Create and activate a virtual environment (Highly Recommended):**
    A virtual environment keeps project dependencies isolated. Open your terminal in the project's root directory.

    *   **Create the virtual environment (e.g., named `venv`):**
        ```bash
        python -m venv venv
        ```
        (If `python` gives "command not found", see Prerequisites above.)

    *   **Activate the virtual environment:**
        *   **On Windows (Command Prompt or PowerShell):**
            ```bash
            venv\Scripts\activate
            ```
            After activation, you should see `(venv)` at the beginning of your terminal prompt.
            *In VS Code terminal, it might activate automatically if VS Code detects the `venv` folder, or you might need to select the interpreter from `venv`.*
            *In Git Bash on Windows, the command might be `source venv/Scripts/activate` (note the slash direction).*

        *   **On macOS and Linux:**
            ```bash
            source venv/bin/activate
            ```
            After activation, you should see `(venv)` at the beginning of your terminal prompt.

3.  **Install dependencies:**
    Once the virtual environment is activated, install the required packages:
    ```bash
    pip install -r requirements.txt
    ```
    (If `pip` gives "command not found" even in an active venv, try `python -m pip install -r requirements.txt`)

4.  **Set up Flask application environment variables:**
    These tell Flask where your application is and optionally enable debug mode.

    *   **On Windows (Command Prompt or PowerShell):**
        ```bash
        set FLASK_APP=app.py
        set FLASK_ENV=development  # Optional: for debug mode and auto-reloading
        ```
        *(Note: `set` variables are usually for the current terminal session only. If you open a new terminal, you'll need to set them again. For PowerShell, you can also use `$env:FLASK_APP = "app.py"`)*

    *   **On macOS and Linux (bash/zsh):**
        ```bash
        export FLASK_APP=app.py
        export FLASK_ENV=development # Optional: for debug mode and auto-reloading
        ```

5.  **Initialize the database:**
    This command needs to be run *once* to create the database file (`game_store.db`) and its tables. Make sure your virtual environment is activated and `FLASK_APP` is set.
    ```bash
    flask init-db
    ```
    **Troubleshooting "flask: command not found":**
    If `flask` is not found even with the virtual environment active, try running it as a Python module:
    ```bash
    python -m flask init-db
    ```

6.  **Run the Flask development server:**
    ```bash
    flask run
    ```
    Or, if `flask` command is not found:
    ```bash
    python -m flask run
    ```
    The application should be accessible at `http://127.0.0.1:5000/` in your web browser.

## Troubleshooting Common "Command Not Found" Issues on Windows

*   **`python` or `pip` not found:**
    *   **Cause:** Python is not installed, or its installation directory was not added to your system's PATH environment variable.
    *   **Solution:** Reinstall Python, ensuring you check "Add Python to PATH" during setup. Alternatively, manually add the Python installation path (e.g., `C:\Users\YourUser\AppData\Local\Programs\Python\Python3X` and `C:\Users\YourUser\AppData\Local\Programs\Python\Python3X\Scripts`) to your system's Environment Variables.

*   **`flask` not found:**
    *   **Cause 1:** Your virtual environment (`venv`) is not activated. The `flask` command is typically available only when the venv where it's installed is active.
    *   **Solution 1:** Ensure you've run `venv\Scripts\activate` (or the correct activation command for your terminal) and see `(venv)` in your prompt.
    *   **Cause 2:** `FLASK_APP` environment variable is not set. While this usually gives a different error, it's good to check.
    *   **Solution 2:** Ensure you've run `set FLASK_APP=app.py`.
    *   **Alternative Solution:** Use `python -m flask <command>` (e.g., `python -m flask run`). This explicitly tells Windows to run flask using the Python interpreter from your active virtual environment.

## Project Structure
(This section remains the same as before)
*   `app.py`: Main Flask application file containing routes and logic.
*   `database_setup.py`: Script to initialize the SQLite database and schema.
*   `game_store.db`: SQLite database file (created after running `flask init-db`).
*   `requirements.txt`: Python package dependencies.
*   `static/`: Contains static files (CSS, JavaScript, images).
    *   `style.css`: Basic stylesheet.
    *   `images/`: Placeholder for game images.
*   `templates/`: Contains HTML templates.
    *   ... (list of templates) ...

## Next Steps / TODO
(This section remains the same as before)
*   ... (list of todos) ...
