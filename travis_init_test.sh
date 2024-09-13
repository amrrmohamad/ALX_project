#!/bin/bash

# Example script to initialize the testing environment and run tests

# Start MySQL service and make database
sudo service mysql start
# OR => run database.py file
python database.py

# Run database migrations or setup scripts if needed
# e.g., python manage.py migrate

# Run tests
pytest

# Alternatively, if using unittest
python -m unittest discover -s tests

# Run Flask framework file
python ST_GitHub.py