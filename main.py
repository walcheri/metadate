import sys
import os
from pathlib import Path
from PySide6.QtWidgets import (QApplication, QMainWindow, QFileDialog, 
                              QMessageBox, QTreeView, QTableView, QLineEdit,
                              QPushButton, QLabel, QVBoxLayout, QHBoxLayout,
                              QWidget, QMenuBar, QStatusBar, QSplitter)
from PySide6.QtCore import QDir, Qt
from PySide6.QtGui import QAction
from core.export_manager import ExportManager
from core.analyzer_engine import AnalyzerEngine
from core.file_tree_model import FileSystemModel
from core.metadata_model import MetadataTableModel

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Metadata Analyzer")
        self.setGeometry(100, 100, 1200, 800)
        
        # Инициализация движка анализа
        self.analyzer_engine = AnalyzerEngine()
        
        # Создание интерфейса
        self.setup_ui()
        
        # Настройка моделей
        self.setup_models()
        
        # Подключение сигналов
        self.connect_signals()
        
    def setup_ui(self):
        """Создание интерфейса программно"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Основной layout
        main_layout = QVBoxLayout(central_widget)
        
        # Панель управления
        control_layout = QHBoxLayout()
        
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("Select folder to analyze...")
        self.path_edit.setMinimumWidth(300)
        
        self.browse_btn = QPushButton("Browse...")
        self.scan_btn = QPushButton("Scan Folder")
        self.export_btn = QPushButton("Export Report")
        self.export_folder_btn = QPushButton("Export Folder Report")
        self.clear_btn = QPushButton("Clear")
        
        control_layout.addWidget(self.path_edit)
        control_layout.addWidget(self.browse_btn)
        control_layout.addWidget(self.scan_btn)
        control_layout.addWidget(self.export_btn)
        control_layout.addWidget(self.export_folder_btn)
        control_layout.addWidget(self.clear_btn)
        
        # Labels для информации
        info_layout = QHBoxLayout()
        self.info_label = QLabel("Ready to analyze")
        self.risk_label = QLabel("Risks: None")
        info_layout.addWidget(self.info_label)
        info_layout.addWidget(self.risk_label)
        
        # File tree и таблица
        splitter = QSplitter(Qt.Horizontal)
        
        self.file_tree = QTreeView()
        self.file_tree.setHeaderHidden(True)
        self.file_tree.setSelectionMode(QTreeView.SingleSelection)
        self.file_tree.setAlternatingRowColors(True)
        
        self.metadata_table = QTableView()
        self.metadata_table.setSelectionBehavior(QTableView.SelectRows)
        self.metadata_table.setSortingEnabled(True)
        self.metadata_table.setAlternatingRowColors(True)
        
        splitter.addWidget(self.file_tree)
        splitter.addWidget(self.metadata_table)
        splitter.setSizes([300, 700])
        
        # Добавление всех элементов в main layout
        main_layout.addLayout(control_layout)
        main_layout.addLayout(info_layout)
        main_layout.addWidget(splitter)
        
        # Создание меню
        self.create_menu()
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
    def create_menu(self):
        """Создание меню"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        open_action = QAction("Open Folder", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.browse_folder)
        file_menu.addAction(open_action)
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def setup_models(self):
        """Настройка моделей данных"""
        self.file_model = FileSystemModel()
        self.file_tree.setModel(self.file_model)
        
        self.metadata_model = MetadataTableModel()
        self.metadata_table.setModel(self.metadata_model)
        
        # Настройка ширины колонок для таблицы
        self.metadata_table.setColumnWidth(0, 150)  # Key
        self.metadata_table.setColumnWidth(1, 250)  # Value
        self.metadata_table.setColumnWidth(2, 100)  # Risk Level
        self.metadata_table.setColumnWidth(3, 150)  # Rule
        self.metadata_table.setColumnWidth(4, 150)  # Source
        
    def connect_signals(self):
        """Подключение сигналов"""
        self.browse_btn.clicked.connect(self.browse_folder)
        self.scan_btn.clicked.connect(self.scan_folder)
        self.export_btn.clicked.connect(self.export_report)
        self.export_folder_btn.clicked.connect(self.export_folder_report)
        self.clear_btn.clicked.connect(self.clear_results)
        self.file_tree.clicked.connect(self.on_file_selected)
        
        
    def browse_folder(self):
        """Открытие диалога выбора папки"""
        folder = QFileDialog.getExistingDirectory(
            self, "Select Folder to Analyze", QDir.homePath()
        )
        if folder:
            self.path_edit.setText(folder)
            self.file_model.setRootPath(folder)
            self.file_tree.setRootIndex(self.file_model.index(folder))
            self.status_bar.showMessage(f"Folder selected: {folder}")
            
    def on_file_selected(self, index):
        """Обработка выбора файла в дереве"""
        if not index.isValid():
            return
            
        file_path = self.file_model.filePath(index)
        if os.path.isfile(file_path):
            self.analyze_single_file(file_path)
            
    def analyze_single_file(self, file_path):
        """Анализ одного файла"""
        try:
            self.status_bar.showMessage(f"Analyzing: {os.path.basename(file_path)}...")
            
            metadata, risks = self.analyzer_engine.analyze_file(file_path)
            self.metadata_model.update_data(metadata, risks)
            self.update_risk_display(risks)
            
            self.status_bar.showMessage(f"Analysis complete: {os.path.basename(file_path)}")
            self.info_label.setText(f"File: {os.path.basename(file_path)}")
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to analyze file: {str(e)}")
            self.status_bar.showMessage("Analysis failed")
            
    def scan_folder(self):
        """Сканирование всей папки"""
        folder_path = self.path_edit.text()
        if not folder_path or not os.path.isdir(folder_path):
            QMessageBox.warning(self, "Warning", "Please select a valid folder first")
            return
            
        try:
            self.status_bar.showMessage("Scanning folder...")
            
            results = self.analyzer_engine.analyze_folder(folder_path)
            self.display_scan_results(results)
            
            self.status_bar.showMessage("Folder scan complete")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Scan failed: {str(e)}")
            self.status_bar.showMessage("Scan failed")
            
    def display_scan_results(self, results):
        """Отображение результатов сканирования папки"""
        total_files = len(results)
        all_metadata = []
        all_risks = []
        
        # Собираем все метаданные и риски из всех файлов
        for file_path, file_data in results.items():
            try:
                metadata = file_data.get('metadata', [])
                risks = file_data.get('risks', [])
                
                # Добавляем информацию о файле к каждому элементу метаданных
                for item in metadata:
                    # Создаем копию элемента с информацией о файле
                    item_with_file = item.copy()
                    item_with_file['file_path'] = file_path
                    item_with_file['file_name'] = os.path.basename(file_path)
                    all_metadata.append(item_with_file)
                
                # Добавляем риски с информацией о файле
                for risk in risks:
                    risk_with_file = risk.copy()
                    risk_with_file['file_path'] = file_path
                    risk_with_file['file_name'] = os.path.basename(file_path)
                    all_risks.append(risk_with_file)
                    
            except Exception as e:
                print(f"Error processing file {file_path} for display: {e}")
        
        # Загружаем все данные в модель
        self.metadata_model.update_data(all_metadata, all_risks)
        
        # Обновляем статистику
        high_risk = sum(1 for file_data in results.values() 
                       if any(r.get('level') == 'high' for r in file_data.get('risks', [])))
        medium_risk = sum(1 for file_data in results.values() 
                         if any(r.get('level') == 'medium' for r in file_data.get('risks', [])))
        low_risk = sum(1 for file_data in results.values() 
                      if any(r.get('level') == 'low' for r in file_data.get('risks', [])))
        
        self.info_label.setText(
            f"Scanned: {total_files} files | "
            f"High risk: {high_risk} | "
            f"Medium risk: {medium_risk} | "
            f"Low risk: {low_risk}"
        )
        
        # Обновляем отображение рисков
        self.update_risk_display(all_risks)
        
    def update_risk_display(self, risks):
        """Обновление информации о рисках"""
        high_risk = sum(1 for r in risks if r['level'] == 'high')
        medium_risk = sum(1 for r in risks if r['level'] == 'medium')
        low_risk = sum(1 for r in risks if r['level'] == 'low')
        
        self.risk_label.setText(
            f"Risks: High ({high_risk}) | Medium ({medium_risk}) | Low ({low_risk})"
        )
        
    def export_report(self):
        """Экспорт отчета"""
        try:
            if not self.metadata_model.rowCount():
                QMessageBox.warning(self, "Warning", "No data to export")
                return
                
            file_path, selected_filter = QFileDialog.getSaveFileName(
                self, "Export Report", "", "HTML Files (*.html);;CSV Files (*.csv)"
            )
            
            if file_path:
                # Получаем данные из модели
                metadata = self.metadata_model._data
                risks = self.metadata_model._risks
                
                success = False
                
                if selected_filter == "HTML Files (*.html)":
                    if not file_path.endswith('.html'):
                        file_path += '.html'
                    success = ExportManager.export_to_html(file_path, metadata, risks)
                    
                elif selected_filter == "CSV Files (*.csv)":
                    if not file_path.endswith('.csv'):
                        file_path += '.csv'
                    success = ExportManager.export_to_csv(file_path, metadata, risks)
                
                if success:
                    QMessageBox.information(self, "Success", 
                        f"Report successfully exported to:\n{file_path}"
                    )
                    # Открываем папку с экспортированным файлом
                    try:
                        import subprocess
                        import os
                        # Безопасное открытие через explorer в Windows
                        if os.name == 'nt':  # Windows
                            subprocess.Popen(['explorer', '/select,', file_path], shell=False)
                        else:  # Linux/Mac
                            subprocess.Popen(['xdg-open', os.path.dirname(file_path)])
                    except Exception:
                        pass
                else:
                    QMessageBox.critical(self, "Error", "Failed to export report")
                    
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Export failed: {str(e)}")
            
    def clear_results(self):
        """Очистка результатов"""
        self.metadata_model.clear_data()
        self.risk_label.setText("Risks: None")
        self.info_label.setText("Ready to analyze")
        self.status_bar.showMessage("Results cleared")
        
    def show_about(self):
        """Показать информацию о программе"""
        QMessageBox.about(self, "About Metadata Analyzer",
            "Metadata Analyzer v1.0\n\n"
            "Tool for analyzing file metadata and detecting "
            "potential information leaks.\n\n"
            "Supports: PDF, DOCX, XLSX, JPEG, PNG, TIFF\n\n"
            "Built with PySide6"
        )
    def export_folder_report(self):
        """Экспорт отчета по всей папке"""
        try:
            folder_path = self.path_edit.text()
            if not folder_path or not os.path.isdir(folder_path):
                QMessageBox.warning(self, "Warning", "Please select a valid folder first")
                return
                
            file_path, selected_filter = QFileDialog.getSaveFileName(
                self, "Export Folder Report", "", "HTML Files (*.html);;CSV Files (*.csv)"
            )
            
            if file_path:
                self.status_bar.showMessage("Analyzing folder for export...")
                
                # Анализируем всю папку
                results = self.analyzer_engine.analyze_folder(folder_path)
                
                if not results:
                    QMessageBox.information(self, "Info", "No risks found in the selected folder")
                    self.status_bar.showMessage("No risks found")
                    return
                
                # Преобразуем результаты в старый формат для экспорта (только риски)
                results_for_export = {}
                for file_path, file_data in results.items():
                    results_for_export[file_path] = file_data.get('risks', [])
                
                success = False
                
                if selected_filter == "HTML Files (*.html)":
                    if not file_path.endswith('.html'):
                        file_path += '.html'
                    success = ExportManager.export_folder_to_html(file_path, results_for_export, folder_path)
                    
                elif selected_filter == "CSV Files (*.csv)":
                    if not file_path.endswith('.csv'):
                        file_path += '.csv'
                    success = ExportManager.export_folder_to_csv(file_path, results_for_export, folder_path)
                
                if success:
                    QMessageBox.information(self, "Success", 
                        f"Folder report successfully exported to:\n{file_path}\n"
                        f"Files analyzed: {len(results)}"
                    )
                    self.status_bar.showMessage("Folder export complete")
                    
                    # Открываем папку с экспортированным файлом
                    try:
                        import subprocess
                        import os
                        # Безопасное открытие через explorer в Windows
                        if os.name == 'nt':  # Windows
                            subprocess.Popen(['explorer', '/select,', file_path], shell=False)
                        else:  # Linux/Mac
                            subprocess.Popen(['xdg-open', os.path.dirname(file_path)])
                    except Exception:
                        pass
                else:
                    QMessageBox.critical(self, "Error", "Failed to export folder report")
                    self.status_bar.showMessage("Folder export failed")
                    
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Folder export failed: {str(e)}")
            self.status_bar.showMessage("Folder export failed")

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Metadata Analyzer")
    app.setApplicationVersion("1.0.0")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
