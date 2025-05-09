from flask import Blueprint, render_template, request, jsonify, current_app, send_file
import os
from app.services.file_service import save_file, get_file_info
from app.services.comparison_service import compare_files
import logging

logger = logging.getLogger(__name__)
main = Blueprint('main', __name__)

@main.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'files' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        
        files = request.files.getlist('files')
        if len(files) != 2:
            return jsonify({'error': 'Please upload exactly two files.'}), 400

        try:
            file_paths = [save_file(file) for file in files]
            file_infos = [get_file_info(path) for path in file_paths]

            logger.debug(f"File infos: {file_infos}")

            output_folder = current_app.config['OUTPUT_FOLDER']
            comparison_result, output_path = compare_files(file_paths[0], file_paths[1], output_folder)

            if isinstance(comparison_result, dict) and 'error' in comparison_result:
                return jsonify(comparison_result), 400

            response_data = {
                'file1': file_infos[0],
                'file2': file_infos[1],
                'result': comparison_result.get('result', ''),
                'summary': comparison_result.get('summary', ''),
                'comparison': comparison_result.get('comparison', []),
                'detailed_analysis': comparison_result.get('detailed_analysis', '')
            }

            if output_path:
                response_data['output_path'] = os.path.basename(output_path)

            logger.debug(f"Response data: {response_data}")
            return jsonify(response_data)
        except Exception as e:
            logger.exception(f"Error processing files: {str(e)}")
            return jsonify({'error': f'An error occurred while processing files: {str(e)}'}), 500

    return render_template('index.html')

@main.route('/download/<filename>')
def download_file(filename):
    try:
        output_folder = current_app.config['OUTPUT_FOLDER']
        file_path = os.path.join(output_folder, filename)
        logger.debug(f"Attempting to download file from: {file_path}")
        
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return jsonify({'error': 'File not found'}), 404
        
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        logger.error(f"Error downloading file: {str(e)}")
        return jsonify({'error': f'An error occurred while downloading the file: {str(e)}'}), 500