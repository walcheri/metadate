import os
from typing import Dict, List, Tuple, Optional
from pathlib import Path
from .parsers.init import get_parser_for_file
from .risk_analyzer import RiskAnalyzer

class AnalyzerEngine:
    def __init__(self):
        self.risk_analyzer = RiskAnalyzer()
        
    def analyze_file(self, file_path: str) -> Tuple[List[Dict], List[Dict]]:
        """Анализ одного файла"""
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        # Определение типа файла по расширению
        mime_type = self._get_mime_type(file_path)
        
        # Получение подходящего парсера
        parser = get_parser_for_file(file_path, mime_type)
        if not parser:
            return [], []
            
        # Извлечение метаданных
        metadata = parser.extract_metadata(file_path)
        
        # Анализ рисков
        risks = self.risk_analyzer.analyze_risks(metadata)
        
        return metadata, risks
        
    def analyze_folder(self, folder_path: str) -> Dict[str, Dict]:
        """Рекурсивный анализ папки
        
        Returns:
            Dict[str, Dict]: Словарь, где ключ - путь к файлу, значение - словарь с 'metadata' и 'risks'
        """
        results = {}
        supported_extensions = {'.pdf', '.docx', '.xlsx', '.jpg', '.jpeg', '.png', '.tiff', '.tif', '.heic', '.heif'}
        MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 MB
        
        try:
            for root, _, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    file_ext = Path(file_path).suffix.lower()
                    
                    if file_ext in supported_extensions:
                        try:
                            # Проверка размера файла
                            file_size = os.path.getsize(file_path)
                            if file_size > MAX_FILE_SIZE:
                                print(f"Skipping large file {file_path} ({file_size / (1024*1024):.1f} MB)")
                                continue
                            
                            # Проверка доступности файла
                            if not os.access(file_path, os.R_OK):
                                print(f"Permission denied: {file_path}")
                                continue
                            
                            metadata, risks = self.analyze_file(file_path)
                            if risks:  # Сохраняем только файлы с рисками
                                results[file_path] = {
                                    'metadata': metadata,
                                    'risks': risks
                                }
                        except PermissionError:
                            print(f"Permission denied: {file_path}")
                        except FileNotFoundError:
                            print(f"File not found (may have been deleted): {file_path}")
                        except OSError as e:
                            print(f"OS error analyzing {file_path}: {e}")
                        except Exception as e:
                            print(f"Error analyzing {file_path}: {e}")
        except PermissionError:
            print(f"Permission denied accessing folder: {folder_path}")
        except Exception as e:
            print(f"Error walking folder {folder_path}: {e}")
                    
        return results
        
    def _get_mime_type(self, file_path: str) -> Optional[str]:
        """Получение MIME-типа файла по расширению"""
        ext = Path(file_path).suffix.lower()
        mime_map = {
            '.pdf': 'application/pdf',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            '.doc': 'application/msword',
            '.xls': 'application/vnd.ms-excel',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.tiff': 'image/tiff',
            '.tif': 'image/tiff',
            '.gif': 'image/gif',
            '.bmp': 'image/bmp',
            '.heic': 'image/heic',  
            '.heif': 'image/heif',  
        }
        return mime_map.get(ext)
