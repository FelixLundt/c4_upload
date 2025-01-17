from flask import Blueprint, render_template, request, flash, redirect, url_for, session, current_app
from app.validator import validate_submission
from app.storage import save_submission, get_group_submissions, delete_oldest_submission, delete_submission, log_message, get_clients
from functools import wraps

bp = Blueprint('upload', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            if not session.get('group_id'):
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
    # Get current submissions
    submissions = get_group_submissions(session['group_id'])
    storage_client, logger = get_clients()
    
    if request.method == 'POST':
        log_message(logger, f"Upload request received for group {session['group_id']}", "INFO", "upload")

        if 'submission' not in request.files:
            flash('Missing submission file')
            log_message(logger, f"Missing submission file for group {session['group_id']}", "ERROR", "upload")
            return redirect(request.url)
            
        submission = request.files['submission']
        
        if submission.filename == '':
            flash('No selected file')
            log_message(logger, f"No selected file for group {session['group_id']}", "ERROR", "upload")
            return redirect(request.url)
            
        if not submission.filename.endswith('.zip'):
            flash('Submission must be a ZIP file')
            log_message(logger, f"Submission must be a ZIP file for group {session['group_id']}", "ERROR", "upload")
            return redirect(request.url)
            
        # Check submission limit
        if len(submissions) >= 2:
            # Delete oldest submission
            log_message(logger, f"Submission limit reached for group {session['group_id']}", "INFO", "upload")
            delete_oldest_submission(session['group_id'])
            flash('Oldest submission was deleted due to limit')

        # Read the entire file for validation
        zip_content = submission.read()
        
        # Validate submission
        validation_result = validate_submission(zip_content)
        if not validation_result['valid']:
            flash(validation_result['message'])
            log_message(logger, f"Submission validation failed for group {session['group_id']}: {validation_result['message']}", "ERROR", "upload")
            return redirect(request.url)
        
        # Save submission
        try:
            submission.seek(0)
            storage_path = save_submission(submission, session['group_id'])
            flash('Submission uploaded successfully')
            
            return redirect(url_for('upload.upload'))
        except Exception as e:
            flash(f'Error saving submission: {str(e)}')
            return redirect(request.url)
    
    return render_template('upload.html', 
                         submissions=submissions,
                         submission_limit=2) 

@bp.route('/delete/<path:submission_path>', methods=['POST'])
@login_required
def delete_submission_route(submission_path):
    storage_client, logger = get_clients()
    if delete_submission(session['group_id'], submission_path):
        flash('Submission deleted successfully')
        log_message(logger, f"Submission deleted successfully for group {session['group_id']}", "INFO", "upload")
    else:
        flash('Error deleting submission')
        log_message(logger, f"Error deleting submission for group {session['group_id']}", "ERROR", "upload")
    return redirect(url_for('upload.upload'))