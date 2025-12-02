from docx import Document
from typing import List, Dict
from .base_parser import BaseParser

class DocxParser(BaseParser):
    
    @staticmethod
    def supported_formats() -> List[str]:
        return [
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/msword'
        ]
        
    def extract_metadata(self, file_path: str) -> List[Dict]:
        metadata = []
        
        try:
            doc = Document(file_path)
            core_props = doc.core_properties
            
            # Основные свойства документа
            properties = {
                'title': core_props.title,
                'subject': core_props.subject,
                'author': core_props.author,
                'last_modified_by': core_props.last_modified_by,
                'created': core_props.created,
                'modified': core_props.modified,
                'keywords': core_props.keywords,
                'category': core_props.category,
                'comments': core_props.comments,
                'revision': core_props.revision,
                'version': core_props.version,
            }
            
            for key, value in properties.items():
                if value:
                    metadata.append(self._format_metadata(key, value))
                    
        except Exception as e:
            print(f"Error reading DOCX metadata: {e}")
            
        return metadata
