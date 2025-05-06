# Connect 4 Tournament Platform

A lightweight web application for managing student submissions and tournament results for a Connect 4 competition.

## Project Structure

```bash
connect4-tournament/
├── app/
│   ├── __init__.py         # Initializes the Flask application and blueprints
│   ├── config.py           # Handles application configuration (e.g., environment variables)
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── upload.py       # Handles agent ZIP file uploads, validation, and team agent limits
│   │   ├── results.py      # (Placeholder) Displays tournament results (e.g., game outcomes, rankings)
│   │   └── downloads.py    # (Placeholder) Handles log file downloads for matches/tournaments
│   ├── storage.py          # Interfaces with Google Cloud Storage for agent storage and retrieval
│   ├── validator.py        # Validates submitted agents against competition rules
│   ├── templates/
│   │   ├── base.html       # Base HTML template for all pages
│   │   ├── upload.html     # HTML for the agent upload page
│   │   └── results.html    # (Placeholder) HTML for the tournament results page
│   └── static/
│       ├── css/            # CSS stylesheets
│       └── js/             # JavaScript files (if any)
├── tests/                  # Unit and integration tests
├── requirements.txt        # Python dependencies for local development
├── main.py                 # Main entry point for the Flask application (used by Gunicorn)
├── .env.example            # Example environment variables file
├── deploy.sh               # Script for deploying the application to Google App Engine
└── README.md
```

## Key Components

1.  **`app/routes/`**: Defines the web endpoints (URLs) that handle HTTP requests.
    *   `upload.py`: Manages the agent submission process. Allows users to upload new agents (up to 2 per team) or update existing ones. Handles agent naming and ensures submissions are in the correct ZIP format.
    *   `results.py`: Intended to display tournament standings and individual game results. (Currently a placeholder)
    *   `downloads.py`: Intended to allow users to download log files from matches or tournaments. (Currently a placeholder)

2.  **`app/storage.py`**: Handles all interactions with Google Cloud Storage.
    *   Stores uploaded agent ZIP files under a structured path: `teams/<team_id>/<agent_name>/<agent_name>.zip`.
    *   Provides functions for saving, retrieving, and deleting agents.
    *   Manages client initialization for Google Cloud Storage and Logging services.

3.  **`app/validator.py`**: Contains logic to validate agent submissions.
    *   **File Structure Check**: Ensures the submitted ZIP file contains `requirements.txt` in the root and an `agent/` package directory.
    *   **Agent Interface Check**: Verifies that the `agent/__init__.py` file exists and that the `agent` module can be imported.
    *   **Function Existence**: Confirms that the `agent` module exposes a callable `generate_move(board, player, timeout)` function.
    *   (Future) Could be extended to run basic tests against the agent or integrate with `c4utils` for more comprehensive validation against game rules.

## Setup and Running Locally

1.  **Prerequisites**:
    *   Python 3.10 or higher.
    *   Google Cloud SDK installed and authenticated (`gcloud auth login`).
    *   A Google Cloud Project with the App Engine Admin API and Cloud Storage API enabled.

2.  **Clone the repository**:
    ```bash
    git clone <repository_url>
    cd connect4-tournament
    ```

3.  **Set up a virtual environment** (recommended):
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

4.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

5.  **Configure Environment Variables**:
    *   Copy `.env.example` to `.env`:
        ```bash
        cp .env.example .env
        ```
    *   Edit `.env` and fill in the required values:
        *   `DOMAIN`: Your custom domain (e.g., `c4league.fans`).
        *   `TEAM1_PASSWORD`, `TEAM2_PASSWORD`, etc.: Passwords for team logins.
        *   `SECRET_KEY`: A strong, random secret key for Flask session management.
        *   `GOOGLE_APPLICATION_CREDENTIALS`: Path to your Google Cloud service account key JSON file (e.g., `connect4-service-key.json`). Download this from the IAM & Admin > Service Accounts section of your GCP project. Ensure the service account has roles like "App Engine Admin" and "Storage Object Admin".

6.  **Run the Flask development server**:
    ```bash
    flask run
    ```
    The application should be accessible at `http://127.0.0.1:5000` (or the port specified by Flask).

## Deployment to Google App Engine

The `deploy.sh` script automates the deployment process to Google App Engine. Make sure to replace team names and passwords in the `deploy.sh` script with your own.

1.  **Prerequisites**:
    *   Google Cloud SDK installed and configured (project set via `gcloud config set project <PROJECT_ID>`).
    *   The `c4utils` package should be located in the parent directory (`../c4utils/`) (available from [here](https://github.com/FelixLundt/c4utils)).
    *   Ensure the service account used by App Engine (usually `<PROJECT_ID>@appspot.gserviceaccount.com`) has necessary permissions (e.g., Storage Object Admin if the app needs to write to buckets beyond its default one, though `storage.py` uses a separate service key for local dev and relies on App Engine default service account permissions when deployed).

2.  **Deployment Steps performed by `deploy.sh`**:
    *   Sets the active GCP project.
    *   Creates a temporary `deploy_tmp` directory.
    *   Copies essential application files (`app/`, `main.py`) to `deploy_tmp`.
    *   Copies the `c4utils` package into `deploy_tmp/c4utils/` so it's available at the root level for App Engine.
    *   Generates a `deploy_tmp/requirements.txt` specifically for deployment, including `gunicorn` and `numpy`, `docker` for `c4utils`.
    *   Generates a `deploy_tmp/app.yaml` with runtime settings, entrypoint (`gunicorn -b :8080 main:app`), and production environment variables.
        *   **Note**: Team passwords and names are currently hardcoded in `deploy.sh` for the `app.yaml` generation. For better security, consider using Secret Manager for sensitive data.
    *   Deploys the contents of `deploy_tmp` to App Engine using `gcloud app deploy`.
    *   Cleans up the `deploy_tmp` directory.

3.  **To deploy manually**:
    *   Ensure your `app.yaml` is configured correctly.
    *   Make sure `c4utils` is in the root of your deployment package if you are not using the script.
    *   Run `gcloud app deploy` from the directory containing `app.yaml` and your application code.

## Important Notes

*   **Security**: The example passwords in `deploy.sh` and `.env.example` are for demonstration only. Use strong, unique passwords and consider integrating a more robust authentication system and managing secrets securely (e.g., Google Cloud Secret Manager).
*   **`c4utils` Dependency**: The application relies on the `c4utils` package. Ensure it's correctly placed or installed for both local development and deployment.