from flask import Blueprint, render_template, request, flash, redirect, url_for
from app.validator import validate_submission
from app.storage import save_submission

bp = Blueprint('upload', __name__)

@bp.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'submission' not in request.files:
            flash('Missing submission file')
            return redirect(request.url)
            
        submission = request.files['submission']
        
        if submission.filename == '':
            flash('No selected file')
            return redirect(request.url)
            
        if not submission.filename.endswith('.zip'):
            flash('Submission must be a ZIP file')
            return redirect(request.url)
            
        # Read the entire file for validation
        zip_content = submission.read()
        
        # Validate submission
        validation_result = validate_submission(zip_content)
        if not validation_result['valid']:
            flash(validation_result['message'])
            return redirect(request.url)
        
        # Save submission (passing the original submission which can be rewound)
        try:
            submission.seek(0)  # Rewind the file pointer
            save_submission(submission)
            flash('Submission uploaded successfully')
            return redirect(url_for('upload.upload'))
        except Exception as e:
            flash(f'Error saving submission: {str(e)}')
            return redirect(request.url)
    
    return render_template('upload.html') 