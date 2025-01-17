import datetime
import os
from google.cloud import storage
from flask import current_app, g
from google.cloud.logging import Client

def get_clients():
    """Get or initialize storage and logging clients using config settings"""
    if 'storage_client' not in g:
        key_path = current_app.config['STORAGE_KEY_PATH']
        
        # Initialize storage client
        if key_path:
            # Development: use service account key file
            g.storage_client = storage.Client.from_service_account_json(key_path)
            g.logging_client = Client.from_service_account_json(key_path)
        else:
            # Production: use default credentials
            g.storage_client = storage.Client()
            g.logging_client = Client()
        
        # Set up logger
        if current_app.debug:
            g.logger = current_app.logger
        else:
            g.logger = g.logging_client.logger("app-log")
            
    return g.storage_client, g.logger

def log_message(logger, message, severity="INFO", component="storage"):
    """Log message using either Cloud Logging or Flask logger"""
    # Check if it's a Cloud Logger by checking for log_struct method
    if hasattr(logger, 'log_struct'):
        logger.log_struct({
            "message": message,
            "severity": severity,
            "component": component
        })
    else:
        if severity == "ERROR":
            logger.error(f"{component}: {message}")
        else:
            logger.info(f"{component}: {message}")

def save_submission(submission_file, group_id):
    """
    Save submission to Google Cloud Storage.
    
    Args:
        submission_file: FileStorage object from Flask
        group_id: String identifier for the submitting group
    
    Returns:
        str: The path where the file was stored
    """
    try:
        storage_client, logger = get_clients()
        log_message(logger, f"Saving submission for group {group_id}", "INFO", "storage")
        
        bucket = storage_client.bucket(current_app.config['STORAGE_BUCKET'])
        
        # Create path with group ID, timestamp and filename
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = submission_file.filename
        storage_path = f'submissions/{group_id}/{timestamp}_{filename}'
        
        # Upload the file
        blob = bucket.blob(storage_path)
        blob.upload_from_file(submission_file)
        
        log_message(logger, f"Submission saved successfully for group {group_id}", "INFO", "storage")

        return storage_path
    except Exception as e:
        _, logger = get_clients()
        log_message(logger, f"Storage error: {str(e)}", "ERROR", "storage")
        raise

def get_group_submissions(group_id):
    """
    Get list of submissions for a group, sorted by timestamp (newest first)
    
    Returns:
        list[dict]: List of submissions with timestamp and filename
    """
    storage_client, _ = get_clients()
    bucket = storage_client.bucket(current_app.config['STORAGE_BUCKET'])
    
    # List all blobs in group's directory
    prefix = f'submissions/{group_id}/'
    blobs = list(bucket.list_blobs(prefix=prefix))
    
    submissions = []
    for blob in blobs:
        # Parse timestamp from filename (format: submissions/group_id/YYYYMMDD_HHMMSS_filename.zip)
        filename = blob.name.split('/')[-1]
        timestamp = datetime.datetime.strptime(filename[:15], '%Y%m%d_%H%M%S')
        
        submissions.append({
            'path': blob.name,
            'filename': filename[16:],  # Remove timestamp prefix
            'timestamp': timestamp,
            'url': blob.public_url if blob.public_url else None
        })
    
    # Sort by timestamp, newest first
    return sorted(submissions, key=lambda x: x['timestamp'], reverse=True)

def delete_oldest_submission(group_id):
    """Delete the oldest submission for a group"""
    submissions = get_group_submissions(group_id)
    if submissions:
        storage_client, _ = get_clients()
        bucket = storage_client.bucket(current_app.config['STORAGE_BUCKET'])
        blob = bucket.blob(submissions[-1]['path'])
        blob.delete()


def delete_submission(group_id, path):
    """
    Delete a specific submission
    
    Args:
        group_id: Group ID for verification
        path: Full storage path of submission to delete
    
    Returns:
        bool: True if deleted, False if not found or not authorized
    """
    # Verify the path belongs to this group
    if not path.startswith(f'submissions/{group_id}/'):
        return False
        
    storage_client, logger = get_clients()
    bucket = storage_client.bucket(current_app.config['STORAGE_BUCKET'])
    blob = bucket.blob(path)
    
    if blob.exists():
        blob.delete()
        log_message(logger, f"Submission deleted successfully for group {group_id}", "INFO", "storage")
        return True
    return False