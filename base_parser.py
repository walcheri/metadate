from abc import ABC, abstractmethod
from typing import Dict, List

class BaseParser(ABC):
    """Абстрактный базовый класс для всех парсеров"""
    
    @staticmethod
    @abstractmethod
    def supported_formats() -> List[str]:
        """Возвращает список поддерживаемых MIME-типов"""
        pass
        
    @abstractmethod
    def extract_metadata(self, file_path: str) -> List[Dict]:
        """Извлекает метаданные из файла"""
        pass
        
    def _format_metadata(self, key: str, value: str, source: str = None) -> Dict:
        """Форматирует метаданные в стандартный вид"""
        return {
            'key': key,
            'value': str(value) if value else '',
            'source': source or self.__class__.__name__
        }