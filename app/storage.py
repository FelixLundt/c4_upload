import datetime
import os
from google.cloud import storage
from flask import current_app

def init_storage_client():
    """Initialize storage client using config settings"""
    return storage.Client.from_service_account_json(current_app.config['STORAGE_KEY_PATH'])

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
        client = init_storage_client()
        bucket = client.bucket(current_app.config['STORAGE_BUCKET'])
        
        # Create path with group ID, timestamp and filename
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = submission_file.filename
        storage_path = f'submissions/{group_id}/{timestamp}_{filename}'
        
        # Upload the file
        blob = bucket.blob(storage_path)
        blob.upload_from_file(submission_file)
        
        return storage_path
    except Exception as e:
        current_app.logger.error(f"Storage error: {str(e)}")
        raise

def get_group_submissions(group_id):
    """
    Get list of submissions for a group, sorted by timestamp (newest first)
    
    Returns:
        list[dict]: List of submissions with timestamp and filename
    """
    client = init_storage_client()
    bucket = client.bucket(current_app.config['STORAGE_BUCKET'])
    
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
        client = init_storage_client()
        bucket = client.bucket(current_app.config['STORAGE_BUCKET'])
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
        
    client = init_storage_client()
    bucket = client.bucket(current_app.config['STORAGE_BUCKET'])
    blob = bucket.blob(path)
    
    if blob.exists():
        blob.delete()
        return True
    return False