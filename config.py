import os

class Config:
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
    OUTPUT_FOLDER = os.path.join(os.getcwd(), 'output')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB