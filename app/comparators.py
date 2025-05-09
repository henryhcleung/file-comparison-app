import os
from PIL import Image
import imagehash
import difflib
import magic
import docx2txt
import PyPDF2
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def compare_files(file1_path, file2_path, output_folder):
    try:
        file_type1 = get_file_type(file1_path)
        file_type2 = get_file_type(file2_path)

        logger.debug(f"File types: {file_type1}, {file_type2}")

        if file_type1 != file_type2:
            return {"error": f"Files are of different types: {file_type1} vs {file_type2}"}, None

        if 'pdf' in file_type1.lower():
            return compare_pdf_files(file1_path, file2_path, output_folder)
        elif 'text' in file_type1 or file_type1 in ['application/vnd.openxmlformats-officedocument.wordprocessingml.document']:
            return compare_text_files(file1_path, file2_path, output_folder, file_type1)
        elif 'image' in file_type1:
            return compare_image_files(file1_path, file2_path, output_folder)
        else:
            return {"error": f"Comparison not supported for file type: {file_type1}"}, None
    except Exception as e:
        logger.exception("Error in compare_files")
        return {"error": f"An error occurred while comparing files: {str(e)}"}, None
    
def compare_pdf_files(file1_path, file2_path, output_folder):
    try:
        text1 = extract_text_from_pdf(file1_path)
        text2 = extract_text_from_pdf(file2_path)
        return compare_text_content(text1, text2, output_folder)
    except Exception as e:
        logger.exception("Error in compare_pdf_files")
        return {"error": f"An error occurred while comparing PDF files: {str(e)}"}, None
    
def compare_text_content(text1, text2, output_folder):
    diff = difflib.ndiff(text1.splitlines(), text2.splitlines())
    result = []
    comparison = []

    for i, s in enumerate(diff):
        if s.startswith('  '):
            result.append(f"Same at line {i}: {s[2:]}")
            comparison.append({"status": "same", "file1": s[2:], "file2": s[2:]})
        elif s.startswith('- '):
            result.append(f"File1 at line {i}: {s[2:]}")
            comparison.append({"status": "different", "file1": s[2:], "file2": ""})
        elif s.startswith('+ '):
            result.append(f"File2 at line {i}: {s[2:]}")
            comparison.append({"status": "different", "file1": "", "file2": s[2:]})

    result_text = "\n".join(result)
    
    output_path = os.path.join(output_folder, "comparison_result.txt")
    with open(output_path, 'w') as f:
        f.write(result_text)

    return {"result": result_text, "comparison": comparison}, output_path


def get_file_type(file_path):
    mime = magic.Magic(mime=True)
    return mime.from_file(file_path)

def compare_text_files(file1_path, file2_path, output_folder, file_type):
    try:
        text1 = extract_text(file1_path, file_type)
        text2 = extract_text(file2_path, file_type)
        return compare_text_content(text1, text2, output_folder)
    except Exception as e:
        logger.exception("Error in compare_text_files")
        return {"error": f"An error occurred while comparing text files: {str(e)}"}, None

def extract_text(file_path, file_type):
    if file_type == 'application/pdf':
        return extract_text_from_pdf(file_path)
    elif file_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
        return docx2txt.process(file_path)
    else:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()

def compare_image_files(file1_path, file2_path, output_folder):
    img1 = Image.open(file1_path)
    img2 = Image.open(file2_path)

    hash1 = imagehash.average_hash(img1)
    hash2 = imagehash.average_hash(img2)

    similarity = 1 - (hash1 - hash2) / len(hash1.hash) ** 2
    
    result = f"Image similarity: {similarity:.2%}\n"
    result += f"Image 1 dimensions: {img1.size}\n"
    result += f"Image 2 dimensions: {img2.size}\n"
    
    if img1.size != img2.size:
        result += "Images have different dimensions\n"
    
    if img1.mode != img2.mode:
        result += f"Images have different color modes: {img1.mode} vs {img2.mode}\n"
    
    output_path = os.path.join(output_folder, "comparison_result.txt")
    with open(output_path, 'w') as f:
        f.write(result)

    summary = f"Image similarity: {similarity:.2%}"
    return {"result": result, "summary": summary}, output_path

def extract_text_from_pdf(pdf_path):
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ''
            for page in reader.pages:
                text += page.extract_text()
        return text
    except Exception as e:
        logger.exception(f"Error extracting text from PDF: {pdf_path}")
        raise