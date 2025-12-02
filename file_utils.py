import os
from pathlib import Path
from typing import List

def get_supported_files(folder_path: str) -> List[str]:
    """Возвращает список поддерживаемых файлов в папке"""
    supported_extensions = {'.pdf', '.docx', '.xlsx', '.jpg', '.jpeg', '.png', '.tiff', '.tif'}
    supported_files = []
    
    for root, _, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            if Path(file_path).suffix.lower() in supported_extensions:
                supported_files.append(file_path)
                
    return supported_files

def is_supported_file(file_path: str) -> bool:
    """Проверяет, поддерживается ли файл для анализа"""
    supported_extensions = {'.pdf', '.docx', '.xlsx', '.jpg', '.jpeg', '.png', '.tiff', '.tif'}
    return Path(file_path).suffix.lower() in supported_extensions

def get_file_size_mb(file_path: str) -> float:
    """Возвращает размер файла в мегабайтах"""
    try:
        return os.path.getsize(file_path) / (1024 * 1024)
    except:
        return 0
