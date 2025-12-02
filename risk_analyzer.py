import re
from typing import List, Dict

class RiskAnalyzer:
    def __init__(self):
        # Правила для определения рисков
        self.rules = [
            # Персональные данные
            {
                'name': 'Author Information',
                'pattern': r'(author|creator|producer|company|organization|username|user(name)?|login)',
                'level': 'medium',
                'case_sensitive': False
            },
            {
                'name': 'Email Addresses',
                'pattern': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                'level': 'high',
                'case_sensitive': False
            },
            {
                'name': 'Phone Numbers',
                'pattern': r'\+7\d{10}',
                'level': 'high',
                'case_sensitive': False
            },
            
            # Пути и местоположения
            {
                'name': 'File Paths',
                'pattern': r'([A-Za-z]:\\[\\\S|*\S]?.*\$|/.*/.*|\\\\.*\\.*)',
                'level': 'high',
                'case_sensitive': False
            },
            {
                'name': 'Internal Network Paths',
                'pattern': r'\\\\[A-Za-z0-9_.-]+\\',
                'level': 'high',
                'case_sensitive': False
            },
            {
                'name': 'Home Directory Paths',
                'pattern': r'(/home/|/Users/|C:\\Users\\|C:\\Documents and Settings\\)',
                'level': 'medium',
                'case_sensitive': False
            },
            
            # Геолокация и координаты
            {
                'name': 'GPS Coordinates',
                'pattern': r'(\d{1,3}°\s\d{1,2}\'\s\d{1,2}\"|\d{1,3}\.\d+\s*[NS]\s*\d{1,3}\.\d+\s*[EW]|\-?\d{1,3}\.\d+,\s*\-?\d{1,3}\.\d+)',
                'level': 'high',
                'case_sensitive': False
            },
            {
                'name': 'GPS EXIF Data',
                'pattern': r'(gps|gpslatitude|gpslongitude|gpsaltitude|geotag|geolocation)',
                'level': 'high',
                'case_sensitive': False
            },
            {
                'name': 'Address Information',
                'pattern': r'(street|st\.|avenue|ave\.|boulevard|blvd\.|road|rd\.|city|town|zip(code)?|postal(code)?)',
                'level': 'medium',
                'case_sensitive': False
            },
            
            # Системная информация
            {
                'name': 'Computer Name',
                'pattern': r'(computername|hostname|machine(name)?)',
                'level': 'medium',
                'case_sensitive': False
            },
            {
                'name': 'IP Addresses',
                'pattern': r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b(?!\s*[\.\d])',
                'level': 'medium',
                'case_sensitive': False
            },
            {
                'name': 'MAC Addresses',
                'pattern': r'([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})',
                'level': 'medium',
                'case_sensitive': False
            },
            
            # Даты и временные метки
            {
                'name': 'Creation Dates',
                'pattern': r'(created|creation(date)?|date.*created|createtime)',
                'level': 'low',
                'case_sensitive': False
            },
            {
                'name': 'Modification Dates',
                'pattern': r'(modified|modification(date)?|date.*modified|lastmodified)',
                'level': 'low',
                'case_sensitive': False
            },
            
            # Программное обеспечение
            {
                'name': 'Software Versions',
                'pattern': r'(version|software|application|appversion|build(number)?)',
                'level': 'low',
                'case_sensitive': False
            },
            {
                'name': 'Office Product IDs',
                'pattern': r'(producer|generator|createdwith|softwareversion)',
                'level': 'low',
                'case_sensitive': False
            },
            
            # Сетевые ресурсы
            {
                'name': 'URLs and Domains',
                'pattern': r'(https?://|www\.|ftp://|\.(com|org|net|ru|com\.ru))',
                'level': 'medium',
                'case_sensitive': False
            },
            {
                'name': 'Server Names',
                'pattern': r'(server|host|database|db(name)?)',
                'level': 'high',
                'case_sensitive': False
            },
            
            # Безопасность и доступ
            {
                'name': 'Password References',
                'pattern': r'(password|passwd|pwd|secret|key|token|auth)',
                'level': 'high',
                'case_sensitive': False
            },
            {
                'name': 'Security Identifiers',
                'pattern': r'(sid|guid|uuid|api[_-]?key)',
                'level': 'high',
                'case_sensitive': False
            },
            
            # Документооборот
            {
                'name': 'Document IDs',
                'pattern': r'(documentid|docid|revision|version(id)?)',
                'level': 'low',
                'case_sensitive': False
            },
            {
                'name': 'Template Paths',
                'pattern': r'(template|normal\.dot(m)?)',
                'level': 'medium',
                'case_sensitive': False
            }
        ]
        
        
    def analyze_risks(self, metadata: List[Dict]) -> List[Dict]:
        """Анализирует метаданные на наличие рисков"""
        risks = []
        
        for item in metadata:
            for rule in self.rules:
                if self._check_rule(item, rule):
                    risk = {
                        'key': item['key'],
                        'value': item['value'],
                        'rule': rule['name'],
                        'level': rule['level'],
                        'source': item['source']
                    }
                    risks.append(risk)
                    
        return risks
        
    def _check_rule(self, metadata_item: Dict, rule: Dict) -> bool:
        """Проверяет одно правило для одного элемента метаданных"""
        flags = 0 if rule.get('case_sensitive', False) else re.IGNORECASE
        
        # Проверяем ключ
        if re.search(rule['pattern'], metadata_item['key'], flags):
            return True
            
        # Проверяем значение
        if re.search(rule['pattern'], str(metadata_item['value']), flags):
            return True
            
        return False
