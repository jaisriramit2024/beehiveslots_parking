# 🐝 Beehive Slots

A simple smart parking system built with Flask.

## Features
- **User Registration**: Register as an Owner or Driver.
- **Owner Panel**: Owners can add parking slots.
- **Driver Booking**: Drivers can view and book available slots.
- **Persistent Storage**: Uses SQLite database (`database.db`).

## How to Run

1.  **Install Flask** (if not already installed):
    ```bash
    pip install flask
    ```

2.  **Run the Application**:
    ```bash
    python app.py
    ```

3.  **Open in Browser**:
    Go to [http://127.0.0.1:5000](http://127.0.0.1:5000)

## Project Structure
- `app.py`: Main backend logic.
- `templates/`: HTML files for valid pages.
- `database.db`: SQLite database file (created automatically).

## Usage Flow
1.  **Register** a new user (e.g., Name: "Alice", Role: "Owner").
2.  Go to **Owner Panel** and add a parking slot.
3.  **Register** another user (e.g., Name: "Bob", Role: "Driver").
4.  Go to **Driver Booking** to see and book the slot.
