# Connect 4 Tournament Platform

A lightweight web application for managing student submissions and tournament results for a Connect 4 competition.

## Project Structure

```bash
connect4-tournament/
├── app/
│ ├── init.py
│ ├── config.py
│ ├── routes/
│ │ ├── init.py
│ │ ├── upload.py # Handles file uploads and validation
│ │ ├── results.py # Displays tournament results
│ │ └── downloads.py # Handles log file downloads
│ ├── storage.py # Interfaces with Google Cloud Storage
│ ├── validator.py # Validates submitted agents
│ ├── templates/
│ │ ├── base.html
│ │ ├── upload.html
│ │ └── results.html
│ └── static/
│ ├── css/
│ └── js/
├── tests/
├── requirements.txt
├── main.py
└── README.md

```

The key components are:

1. **routes/**: The web endpoints that handle HTTP requests
   - Organizes the different pages/features of the application
   - Coordinates between storage, validation, and display

2. **storage.py**: Handles all Google Cloud Storage operations
   - Uploading student submissions
   - Retrieving tournament results
   - Managing log files

3. **validator.py**: Contains all validation logic
   - Checks submission format
   - Verifies agent interface compliance
   - Runs basic tests
   - Integrates with tournament rules