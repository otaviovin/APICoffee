# Cafe API

This is a Flask-based RESTful API for managing a database of cafes. The API provides functionality to add, retrieve, update, and delete cafes. The cafes are stored in a SQLite database, and each cafe entry includes details like its name, location, amenities, and coffee price.

## Features

- Retrieve a random cafe.
- Get a list of all cafes.
- Search for cafes by location.
- Add a new cafe.
- Update the price of a specific cafe.
- Delete a cafe (requires an API key).

## Prerequisites

Before running the project, ensure you have the following installed:

- Python 3.x
- Flask
- Flask-SQLAlchemy

Install the required packages by running the following command:

### On Windows:
```bash
python -m pip install -r requirements.txt
