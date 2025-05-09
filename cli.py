import argparse
from app.comparators import compare_files
from utils.file_utils import get_platform_info
import os

def main():
    parser = argparse.ArgumentParser(description='File Comparison Tool')
    parser.add_argument('file1', type=str, help='Path to the first file')
    parser.add_argument('file2', type=str, help='Path to the second file')
    args = parser.parse_args()

    file1_path = args.file1
    file2_path = args.file2

    if not os.path.exists(file1_path) or not os.path.exists(file2_path):
        print("One or both files do not exist.")
        return

    result = compare_files(file1_path, file2_path)
    platform = get_platform_info()
    
    print("Comparison Result:")
    print(f"Platform: {platform}")
    print(result)

if __name__ == '__main__':
    main()