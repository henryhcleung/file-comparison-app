import os
from werkzeug.utils import secure_filename
import magic

def save_file(file, upload_folder):
    filename = secure_filename(file.filename)
    file_path = os.path.join(upload_folder, filename)
    file.save(file_path)
    return filename

def get_file_type(file_path):
    mime = magic.Magic(mime=True)
    return mime.from_file(file_path)