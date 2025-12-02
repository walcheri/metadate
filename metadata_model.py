from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex
from PySide6.QtGui import QColor

class MetadataTableModel(QAbstractTableModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._data = []  # Список метаданных
        self._risks = [] # Список рисков
        self._headers = ['Key', 'Value', 'Risk Level', 'Rule', 'Source']
        
    def rowCount(self, parent=QModelIndex()):
        return len(self._data)
        
    def columnCount(self, parent=QModelIndex()):
        return len(self._headers)
        
    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
            
        row, col = index.row(), index.column()
        
        # Проверка границ
        if row < 0 or row >= len(self._data):
            return None
        
        if role == Qt.DisplayRole:
            item = self._data[row]
            if not isinstance(item, dict):
                return None
                
            if col == 0:
                return item.get('key', '')
            elif col == 1:
                value = item.get('value', '')
                value_str = str(value) if value is not None else ''
                return value_str[:100] + "..." if len(value_str) > 100 else value_str
            elif col == 2:
                risk = self._get_risk_for_item(item)
                return risk.get('level', 'None') if risk else 'None'
            elif col == 3:
                risk = self._get_risk_for_item(item)
                return risk.get('rule', '') if risk else ''
            elif col == 4:
                return item.get('source', '')
                
        elif role == Qt.BackgroundRole:
            item = self._data[row]
            if not isinstance(item, dict):
                return None
            risk = self._get_risk_for_item(item)
            if risk and isinstance(risk, dict):
                level = risk.get('level', '')
                if level == 'high':
                    return QColor(255, 200, 200)  # Светло-красный
                elif level == 'medium':
                    return QColor(255, 255, 200)  # Светло-желтый
                elif level == 'low':
                    return QColor(200, 255, 200)  # Светло-зеленый

        elif role == Qt.ForegroundRole:  # Цвет текста
            item = self._data[row]
            if not isinstance(item, dict):
                return None
            risk = self._get_risk_for_item(item)
            if risk and isinstance(risk, dict):
                return QColor(0, 0, 0)  # Черный текст для всех рисков        
                    
        elif role == Qt.ToolTipRole:
            if col == 1:
                item = self._data[row]
                if isinstance(item, dict):
                    value = item.get('value', '')
                    return str(value) if value is not None else ''
                
        return None
        
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if 0 <= section < len(self._headers):
                return self._headers[section]
        return None
        
    def update_data(self, metadata: list, risks: list):
        self.beginResetModel()
        self._data = metadata
        self._risks = risks
        self.endResetModel()
        
    def clear_data(self):
        self.beginResetModel()
        self._data = []
        self._risks = []
        self.endResetModel()
        
    def _get_risk_for_item(self, item: dict) -> dict:
        """Находит риск для элемента метаданных"""
        if not isinstance(item, dict):
            return None
            
        item_key = item.get('key')
        item_value = item.get('value')
        item_source = item.get('source')
        
        for risk in self._risks:
            if not isinstance(risk, dict):
                continue
            if (risk.get('key') == item_key and 
                risk.get('value') == item_value and 
                risk.get('source') == item_source):
                return risk
        return None
