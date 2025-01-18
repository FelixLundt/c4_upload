from google.cloud import storage
from google.cloud.logging import Client
from flask import current_app, g
import os

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

def get_bucket():
    """Get the storage bucket."""
    storage_client, _ = get_clients()
    return storage_client.bucket(current_app.config['STORAGE_BUCKET'])

def save_agent(file, group_name, agent_name, is_update):
    """
    Save an agent to Google Cloud Storage.
    Returns the cloud storage path on success, None on failure.
    """
    try:
        _, logger = get_clients()
        bucket = get_bucket()
        team_agents = get_team_agents(group_name)
        agent_version = [agent_dict['version'] for agent_dict in team_agents if agent_dict['name'] == agent_name]
        if len(agent_version) == 0 and is_update:
            raise KeyError('Agent unknown, can\'t update.')
        if len(agent_version) > 0 and not is_update:
            raise KeyError('Agent already exists, can\'t upload.')
        new_version = int(agent_version[0]) + 1 if is_update else 1
        blob_path = f"submissions/{group_name}/{agent_name}/{agent_name}_v{new_version}.zip"
        blob = bucket.blob(blob_path)
        blob.upload_from_file(file)
        log_message(logger, f"Agent {agent_name} (version {new_version}) saved successfully for team {group_name}")
        return blob_path
    except Exception as e:
        _, logger = get_clients()
        log_message(logger, f"Error saving agent: {str(e)}", "ERROR")
        return None

def delete_agent(group_name, agent_name):
    """
    Delete an agent and its directory from Google Cloud Storage.
    Returns True on success, False on failure.
    """
    try:
        storage_client, logger = get_clients()
        bucket = get_bucket()
        prefix = f"submissions/{group_name}/{agent_name}/"
        blobs = bucket.list_blobs(prefix=prefix)
        for blob in blobs:
            blob.delete()
        log_message(logger, f"Agent {agent_name} deleted successfully for team {group_name}")
        return True
    except Exception as e:
        storage_client, logger = get_clients()
        log_message(logger, f"Error deleting agent: {str(e)}", "ERROR")
        return False

def get_team_agents(group_name):
    """
    Get list of agents for a team.
    Returns a list of agent dictionaries with name and path.
    """
    try:
        _, logger = get_clients()
        bucket = get_bucket()
        team_prefix = f"submissions/{group_name}/"
        blobs = bucket.list_blobs(prefix=team_prefix)
        agents = []
        for blob in blobs:
            print(blob.name)
            # Extract agent name from prefix (submissions/group_name/agent_name/agent-name_v1.zip)
            agent_name_version = blob.name.split('/')[-1].strip('.zip')
            agent_name, version = agent_name_version.split('_')
            version = version[1:] # Get 'v..' after underscore, remove the 'v' from the version
            
            if blob.exists():
                agents.append({
                    'name': agent_name,
                    'version': version,
                    'path': f"{blob.name}"
                })
        
        log_message(logger, f"Retrieved {len(agents)} agents for team {group_name}")
        return agents
    except Exception as e:
        _, logger = get_clients()
        log_message(logger, f"Error listing agents: {str(e)}", "ERROR")
        return []