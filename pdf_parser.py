import PyPDF2
from typing import List, Dict
from .base_parser import BaseParser

class PDFParser(BaseParser):
    
    @staticmethod
    def supported_formats() -> List[str]:
        return ['application/pdf']
        
    def extract_metadata(self, file_path: str) -> List[Dict]:
        metadata = []
        
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                doc_info = pdf_reader.metadata
                
                if doc_info:
                    for key, value in doc_info.items():
                        # Убираем префикс '/', если есть
                        clean_key = key[1:] if key.startswith('/') else key
                        metadata.append(self._format_metadata(clean_key, value))
                        
                # Добавляем информацию о документе
                metadata.append(self._format_metadata('Pages', len(pdf_reader.pages)))
                metadata.append(self._format_metadata('Encrypted', pdf_reader.is_encrypted))
                
        except Exception as e:
            print(f"Error reading PDF metadata: {e}")
            
        return metadata
