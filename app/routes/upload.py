from flask import Blueprint, render_template, request, flash, redirect, url_for, session, current_app
from werkzeug.utils import secure_filename
from functools import wraps
import re
from ..storage import get_clients, save_agent, delete_agent, get_team_agents, log_message
from ..validator import validate_submission

bp = Blueprint('upload', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            if not session.get('group_name'):
                flash('Please log in first')
                return redirect(url_for('auth.login'))
        except RuntimeError as e:
            current_app.logger.error(f"Session error: {str(e)}")
            return "Session error. Please try again.", 500
        except Exception as e:
            current_app.logger.error(f"Unexpected error in login check: {str(e)}")
            return "Server error", 500
            
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    # Get current agents and initialize logging
    storage_client, logger = get_clients()
    group_name = session['group_name']
    agents = get_team_agents(group_name)
    
    if request.method == 'POST':
        log_message(logger, f"Upload request received from {group_name}", "INFO", "upload")
        
        if 'submission' not in request.files:
            flash('No file uploaded')
            log_message(logger, "No file in request", "ERROR", "upload")
            return redirect(request.url)
        
        file = request.files['submission']
        if file.filename == '':
            flash('No file selected')
            log_message(logger, "Empty filename", "ERROR", "upload")
            return redirect(request.url)
        
        if not file.filename.endswith('.zip'):
            flash('Please upload a ZIP file')
            log_message(logger, "Invalid file type", "ERROR", "upload")
            return redirect(request.url)
        
        if 'agent_name' not in request.form:
            flash('Please provide a name for your agent')
            log_message(logger, "No agent name provided", "ERROR", "upload")
            return redirect(request.url)
        
        agent_name = secure_filename(request.form['agent_name'].strip())
        # Validate agent name
        if not re.match(r'^[A-Za-z0-9-]+$', agent_name):
            flash('Agent name can only contain letters, numbers, and hyphens')
            log_message(logger, "Invalid agent name", "ERROR", "upload")
            return redirect(request.url)
        
        if not agent_name:
            flash('Agent name cannot be empty')
            log_message(logger, "Empty agent name", "ERROR", "upload")
            return redirect(request.url)

        
        
        # Check if this is an update or new upload
        is_update = any(agent['name'] == agent_name for agent in agents)
        
        if not is_update:
            # Check if we're at the agent limit for new uploads
            if len(agents) >= 2:
                flash('You can only have up to 2 agents. Please delete one first.')
                log_message(logger, f"Agent limit reached for {group_name}", "INFO", "upload")
                return redirect(request.url)
        
        # Read the entire file for validation
        zip_content = file.read()
        
        # Validate submission
        validation_result = validate_submission(zip_content)
        if not validation_result['valid']:
            flash(f"Invalid submission: {validation_result['message']}")
            log_message(logger, f"Validation failed: {validation_result['message']}", "ERROR", "upload")
            return redirect(request.url)
        
        # Reset file pointer after validation
        file.seek(0)
        
        # Save the agent
        storage_path = save_agent(file, group_name, agent_name, is_update)
        if storage_path:
            if is_update:
                flash(f'Agent "{agent_name}" updated successfully')
                log_message(logger, f"Agent {agent_name} updated successfully", "INFO", "upload")
            else:
                flash(f'Agent "{agent_name}" uploaded successfully')
                log_message(logger, f"Agent {agent_name} uploaded successfully", "INFO", "upload")
        else:
            flash('Error saving agent')
            # save_agent already logs the error
        print(agents)
        return redirect(url_for('upload.upload'))
    
    return render_template('upload.html',
                         agents=agents)

@bp.route('/delete/<agent_name>', methods=['POST'])
@login_required
def delete_agent_route(agent_name):
    storage_client, logger = get_clients()
    group_name = session['group_name']
    
    if delete_agent(group_name, agent_name):
        flash('Agent deleted successfully')
        log_message(logger, f"Agent {agent_name} deleted successfully", "INFO", "upload")
    else:
        flash('Error deleting agent')
        # delete_agent already logs the error
    
    return redirect(url_for('upload.upload'))