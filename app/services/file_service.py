import os
import magic
from flask import current_app
from werkzeug.utils import secure_filename

def save_file(file):
    filename = secure_filename(file.filename)
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    return filepath

def get_file_info(file_path):
    mime = magic.Magic(mime=True)
    file_type = mime.from_file(file_path)
    file_size = os.path.getsize(file_path)
    file_extension = os.path.splitext(file_path)[1][1:]  # Get extension without dot
    return {
        'name': os.path.basename(file_path),
        'type': file_type,
        'size': file_size,
        'extension': file_extension,
        'origin': 'Uploaded from user device'
    }