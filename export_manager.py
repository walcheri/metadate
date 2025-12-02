import csv
import os
from datetime import datetime
from typing import List, Dict
from pathlib import Path

class ExportManager:
    @staticmethod
    def export_to_html(file_path: str, data: List[Dict], risks: List[Dict]):
        """Экспорт данных в HTML файл"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('<!DOCTYPE html>\n')
                f.write('<html>\n')
                f.write('<head>\n')
                f.write('    <meta charset="UTF-8">\n')
                f.write('    <title>Metadata Analysis Report</title>\n')
                f.write('    <style>\n')
                f.write('        body { font-family: Arial, sans-serif; margin: 20px; }\n')
                f.write('        h1 { color: #333; }\n')
                f.write('        table { border-collapse: collapse; width: 100%; margin-bottom: 20px; }\n')
                f.write('        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }\n')
                f.write('        th { background-color: #f2f2f2; }\n')
                f.write('        .high-risk { background-color: #ffcccc; }\n')
                f.write('        .medium-risk { background-color: #ffffcc; }\n')
                f.write('        .low-risk { background-color: #ccffcc; }\n')
                f.write('        .risk-badge { padding: 2px 6px; border-radius: 3px; font-size: 12px; }\n')
                f.write('    </style>\n')
                f.write('</head>\n')
                f.write('<body>\n')
                
                f.write(f'    <h1>Metadata Analysis Report</h1>\n')
                f.write(f'    <p>Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>\n')
                f.write(f'    <p>Total metadata items: {len(data)}</p>\n')
                f.write(f'    <p>Total risks found: {len(risks)}</p>\n')
                
                # Статистика по рискам
                risk_stats = {
                    'high': sum(1 for r in risks if r['level'] == 'high'),
                    'medium': sum(1 for r in risks if r['level'] == 'medium'),
                    'low': sum(1 for r in risks if r['level'] == 'low')
                }
                
                f.write(f'    <p>Risk statistics: High ({risk_stats["high"]}), Medium ({risk_stats["medium"]}), Low ({risk_stats["low"]})</p>\n')
                
                # Таблица метаданных
                f.write('    <h2>Metadata</h2>\n')
                f.write('    <table>\n')
                f.write('        <tr>\n')
                f.write('            <th>Key</th>\n')
                f.write('            <th>Value</th>\n')
                f.write('            <th>Source</th>\n')
                f.write('            <th>Risk Level</th>\n')
                f.write('        </tr>\n')
                
                for item in data:
                    risk = next((r for r in risks if r['key'] == item['key'] and r['value'] == item['value']), None)
                    risk_class = f'class="{risk["level"]}-risk"' if risk and risk.get('level') else ''
                    risk_badge = f'<span class="risk-badge {risk["level"]}-risk">{risk["level"].upper()}</span>' if risk and risk.get('level') else 'None'
                    
                    f.write(f'        <tr {risk_class}>\n')
                    f.write(f'            <td>{item["key"]}</td>\n')
                    f.write(f'            <td>{item["value"]}</td>\n')
                    f.write(f'            <td>{item["source"]}</td>\n')
                    f.write(f'            <td>{risk_badge}</td>\n')
                    f.write('        </tr>\n')
                
                f.write('    </table>\n')
                
                # Детали рисков
                if risks:
                    f.write('    <h2>Risk Details</h2>\n')
                    f.write('    <table>\n')
                    f.write('        <tr>\n')
                    f.write('            <th>Key</th>\n')
                    f.write('            <th>Value</th>\n')
                    f.write('            <th>Risk Level</th>\n')
                    f.write('            <th>Rule</th>\n')
                    f.write('            <th>Source</th>\n')
                    f.write('        </tr>\n')
                    
                    for risk in risks:
                        f.write(f'        <tr class="{risk["level"]}-risk">\n')
                        f.write(f'            <td>{risk["key"]}</td>\n')
                        f.write(f'            <td>{risk["value"]}</td>\n')
                        f.write(f'            <td>{risk["level"].upper()}</td>\n')
                        f.write(f'            <td>{risk["rule"]}</td>\n')
                        f.write(f'            <td>{risk["source"]}</td>\n')
                        f.write('        </tr>\n')
                    
                    f.write('    </table>\n')
                
                f.write('</body>\n')
                f.write('</html>\n')
            
            return True
        except Exception as e:
            print(f"Error exporting to HTML: {e}")
            return False
    @staticmethod
    def export_folder_to_html(file_path: str, results: Dict[str, List[Dict]], folder_path: str):
        """Экспорт отчета по папке в HTML"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('<!DOCTYPE html>\n')
                f.write('<html>\n')
                f.write('<head>\n')
                f.write('    <meta charset="UTF-8">\n')
                f.write('    <title>Folder Metadata Analysis Report</title>\n')
                f.write('    <style>\n')
                f.write('        body { font-family: Arial, sans-serif; margin: 20px; }\n')
                f.write('        h1 { color: #333; }\n')
                f.write('        h2 { color: #555; margin-top: 30px; }\n')
                f.write('        table { border-collapse: collapse; width: 100%; margin-bottom: 20px; }\n')
                f.write('        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }\n')
                f.write('        th { background-color: #f2f2f2; }\n')
                f.write('        .high-risk { background-color: #ffcccc; }\n')
                f.write('        .medium-risk { background-color: #ffffcc; }\n')
                f.write('        .low-risk { background-color: #ccffcc; }\n')
                f.write('        .risk-badge { padding: 2px 6px; border-radius: 3px; font-size: 12px; }\n')
                f.write('        .file-section { margin-bottom: 30px; padding: 15px; border: 1px solid #eee; }\n')
                f.write('    </style>\n')
                f.write('</head>\n')
                f.write('<body>\n')
                
                f.write(f'    <h1>Folder Metadata Analysis Report</h1>\n')
                f.write(f'    <p>Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>\n')
                f.write(f'    <p>Folder: {folder_path}</p>\n')
                f.write(f'    <p>Total files with risks: {len(results)}</p>\n')
                
                # Общая статистика
                total_risks = 0
                risk_stats = {'high': 0, 'medium': 0, 'low': 0}
                
                for file_risks in results.values():
                    total_risks += len(file_risks)
                    for risk in file_risks:
                        risk_stats[risk['level']] += 1
                
                f.write(f'    <p>Total risks found: {total_risks}</p>\n')
                f.write(f'    <p>Risk statistics: High ({risk_stats["high"]}), Medium ({risk_stats["medium"]}), Low ({risk_stats["low"]})</p>\n')
                
                # Отчет по каждому файлу
                for file_path, risks in results.items():
                    f.write(f'    <div class="file-section">\n')
                    f.write(f'        <h2>File: {os.path.basename(file_path)}</h2>\n')
                    f.write(f'        <p>Path: {file_path}</p>\n')
                    f.write(f'        <p>Risks found: {len(risks)}</p>\n')
                    
                    # Таблица рисков для файла
                    f.write('        <table>\n')
                    f.write('            <tr>\n')
                    f.write('                <th>Key</th>\n')
                    f.write('                <th>Value</th>\n')
                    f.write('                <th>Risk Level</th>\n')
                    f.write('                <th>Rule</th>\n')
                    f.write('                <th>Source</th>\n')
                    f.write('            </tr>\n')
                    
                    for risk in risks:
                        f.write(f'            <tr class="{risk["level"]}-risk">\n')
                        f.write(f'                <td>{risk["key"]}</td>\n')
                        f.write(f'                <td>{risk["value"]}</td>\n')
                        f.write(f'                <td><span class="risk-badge {risk["level"]}-risk">{risk["level"].upper()}</span></td>\n')
                        f.write(f'                <td>{risk["rule"]}</td>\n')
                        f.write(f'                <td>{risk["source"]}</td>\n')
                        f.write('            </tr>\n')
                    
                    f.write('        </table>\n')
                    f.write('    </div>\n')
                
                f.write('</body>\n')
                f.write('</html>\n')
            
            return True
        except Exception as e:
            print(f"Error exporting folder to HTML: {e}")
            return False

    @staticmethod
    def export_folder_to_csv(file_path: str, results: Dict[str, List[Dict]], folder_path: str):
        """Экспорт отчета по папке в CSV"""
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # Заголовок
                writer.writerow(['Folder Metadata Analysis Report'])
                writer.writerow([f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'])
                writer.writerow([f'Folder: {folder_path}'])
                writer.writerow([f'Total files with risks: {len(results)}'])
                writer.writerow([])
                
                # Общая статистика
                total_risks = 0
                risk_stats = {'high': 0, 'medium': 0, 'low': 0}
                
                for file_risks in results.values():
                    total_risks += len(file_risks)
                    for risk in file_risks:
                        risk_stats[risk['level']] += 1
                
                writer.writerow([f'Total risks found: {total_risks}'])
                writer.writerow(['Risk statistics:', f'High: {risk_stats["high"]}', f'Medium: {risk_stats["medium"]}', f'Low: {risk_stats["low"]}'])
                writer.writerow([])
                
                # Данные по каждому файлу
                for file_path, risks in results.items():
                    writer.writerow([f'FILE: {os.path.basename(file_path)}'])
                    writer.writerow(['File path:', file_path])
                    writer.writerow(['Risks found:', len(risks)])
                    writer.writerow([])
                    
                    writer.writerow(['Key', 'Value', 'Risk Level', 'Rule', 'Source'])
                    
                    for risk in risks:
                        writer.writerow([
                            risk['key'],
                            risk['value'],
                            risk['level'].upper(),
                            risk['rule'],
                            risk['source']
                        ])
                    
                    writer.writerow([])
                    writer.writerow([])
                
            return True
        except Exception as e:
            print(f"Error exporting folder to CSV: {e}")
            return False
        
    @staticmethod
    def export_to_csv(file_path: str, data: List[Dict], risks: List[Dict]):
        """Экспорт данных в CSV файл"""
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # Заголовок
                writer.writerow(['Metadata Analysis Report'])
                writer.writerow([f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'])
                writer.writerow([f'Total metadata items: {len(data)}'])
                writer.writerow([f'Total risks found: {len(risks)}'])
                writer.writerow([])
                
                # Статистика рисков
                risk_stats = {
                    'high': sum(1 for r in risks if r['level'] == 'high'),
                    'medium': sum(1 for r in risks if r['level'] == 'medium'),
                    'low': sum(1 for r in risks if r['level'] == 'low')
                }
                writer.writerow(['Risk statistics:', f'High: {risk_stats["high"]}', f'Medium: {risk_stats["medium"]}', f'Low: {risk_stats["low"]}'])
                writer.writerow([])
                
                # Метаданные
                writer.writerow(['METADATA'])
                writer.writerow(['Key', 'Value', 'Source', 'Risk Level'])
                
                for item in data:
                    risk = next((r for r in risks if r['key'] == item['key'] and r['value'] == item['value']), None)
                    risk_level = risk['level'].upper() if risk and risk.get('level') else 'None'
                    
                    writer.writerow([
                        item['key'],
                        item['value'],
                        item['source'],
                        risk_level
                    ])
                
                writer.writerow([])
                
                # Детали рисков
                if risks:
                    writer.writerow(['RISK DETAILS'])
                    writer.writerow(['Key', 'Value', 'Risk Level', 'Rule', 'Source'])
                    
                    for risk in risks:
                        writer.writerow([
                            risk['key'],
                            risk['value'],
                            risk['level'].upper(),
                            risk['rule'],
                            risk['source']
                        ])
            
            return True
        except Exception as e:
            print(f"Error exporting to CSV: {e}")
            return False
