from PySide6.QtCore import QDir, QModelIndex, Qt
from PySide6.QtWidgets import QFileSystemModel 

class FileSystemModel(QFileSystemModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFilter(QDir.AllEntries | QDir.NoDotAndDotDot | QDir.Hidden)
        
    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and index.column() == 0:
            file_path = self.filePath(index)
            return QDir.toNativeSeparators(file_path)
        return super().data(index, role)
