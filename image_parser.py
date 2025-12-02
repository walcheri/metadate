import exifread
from PIL import Image, ExifTags
from typing import List, Dict
from .base_parser import BaseParser
import datetime
import os
from pathlib import Path

class ImageParser(BaseParser):
    
    @staticmethod
    def supported_formats() -> List[str]:
        return [
            'image/jpeg',
            'image/tiff',
            'image/png',
            'image/webp',
            'image/gif',
            'image/bmp'
        ]
        
    def extract_metadata(self, file_path: str) -> List[Dict]:
        metadata = []
        
        try:
            # Сначала получаем базовую информацию о файле
            file_info = self._get_file_info(file_path)
            for key, value in file_info.items():
                metadata.append(self._format_metadata(key, value))
            
            # EXIF данные через exifread
            exif_metadata = self._extract_exif_with_exifread(file_path)
            metadata.extend(exif_metadata)
            
            # EXIF через PIL (если доступно)
            pil_metadata = self._extract_exif_with_pil(file_path)
            metadata.extend(pil_metadata)
            
            # Информация о изображении через PIL
            image_metadata = self._extract_image_info(file_path)
            metadata.extend(image_metadata)
            
            # Дополнительная техническая информация
            tech_metadata = self._extract_technical_info(file_path)
            metadata.extend(tech_metadata)
                    
        except Exception as e:
            print(f"Error reading image metadata: {e}")
            # Возвращаем хотя бы базовую информацию
            file_info = self._get_file_info(file_path)
            for key, value in file_info.items():
                metadata.append(self._format_metadata(key, value))
            
        return metadata
    
    def _get_file_info(self, file_path: str) -> Dict[str, str]:
        """Базовая информация о файле"""
        try:
            stat = os.stat(file_path)
            return {
                'File Name': os.path.basename(file_path),
                'File Size': f"{stat.st_size} bytes ({stat.st_size / 1024:.1f} KB)",
                'File Extension': Path(file_path).suffix,
                'File Path': file_path,
                'File Created': datetime.datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S'),
                'File Modified': datetime.datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                'File Accessed': datetime.datetime.fromtimestamp(stat.st_atime).strftime('%Y-%m-%d %H:%M:%S'),
            }
        except Exception as e:
            return {'Error': f'File info error: {e}'}
    
    def _extract_exif_with_exifread(self, file_path: str) -> List[Dict]:
        """Извлекает EXIF данные через exifread"""
        metadata = []
        try:
            with open(file_path, 'rb') as f:
                tags = exifread.process_file(f, details=False)
                for tag, value in tags.items():
                    if tag not in ('JPEGThumbnail', 'TIFFThumbnail', 'Filename'):
                        clean_value = str(value)
                        # Специальная обработка для некоторых полей
                        if 'GPS' in tag:
                            clean_value = self._format_gps_value(tag, clean_value)
                        metadata.append(self._format_metadata(f'EXIF_{tag}', clean_value))
        except Exception as e:
            print(f"Error with exifread: {e}")
        return metadata
    
    def _extract_exif_with_pil(self, file_path: str) -> List[Dict]:
        """Извлекает EXIF данные через PIL"""
        metadata = []
        try:
            image = Image.open(file_path)
            # Используем getexif() если доступно, иначе _getexif()
            if hasattr(image, 'getexif'):
                exif_data = image.getexif()
            elif hasattr(image, '_getexif'):
                exif_data = image._getexif()
            else:
                exif_data = None
            
            if exif_data:
                for tag_id, value in exif_data.items():
                    tag_name = ExifTags.TAGS.get(tag_id, f'Unknown_{tag_id}')
                    if value:
                        formatted_value = self._format_exif_value(tag_name, value)
                        metadata.append(self._format_metadata(f'EXIF_{tag_name}', formatted_value))
        except Exception as e:
            print(f"Error with PIL EXIF: {e}")
        return metadata
    
    def _extract_image_info(self, file_path: str) -> List[Dict]:
        """Извлекает информацию о изображении"""
        metadata = []
        try:
            with Image.open(file_path) as img:
                image_info = {
                    'Image Width': img.width,
                    'Image Height': img.height,
                    'Image Mode': img.mode,
                    'Image Format': img.format,
                    'Image Bands': ', '.join(img.getbands()) if hasattr(img, 'getbands') else 'N/A',
                    'Image Palette': 'Yes' if img.palette else 'No',
                    'Image Animated': 'Yes' if getattr(img, 'is_animated', False) else 'No',
                    'Image Frames': getattr(img, 'n_frames', 1),
                }
                
                # Цветовой профиль
                if hasattr(img, 'info') and 'icc_profile' in img.info:
                    image_info['Color Profile'] = 'Present'
                
                for key, value in image_info.items():
                    if value:
                        metadata.append(self._format_metadata(key, str(value)))
                        
        except Exception as e:
            print(f"Error extracting image info: {e}")
        return metadata
    
    def _extract_technical_info(self, file_path: str) -> List[Dict]:
        """Извлекает техническую информацию"""
        metadata = []
        try:
            with Image.open(file_path) as img:
                # Информация о сжатии
                if hasattr(img, 'info'):
                    for key, value in img.info.items():
                        if key not in ('icc_profile', 'exif'):  # Исключаем уже обработанные
                            if key == 'dpi':
                                metadata.append(self._format_metadata('Resolution', f'{value} DPI'))
                            elif key == 'compression':
                                metadata.append(self._format_metadata('Compression', value))
                            else:
                                metadata.append(self._format_metadata(f'Tech_{key}', str(value)))
                
                # Ориентация
                try:
                    # Используем getexif() если доступно, иначе _getexif()
                    if hasattr(img, 'getexif'):
                        exif = img.getexif()
                    elif hasattr(img, '_getexif'):
                        exif = img._getexif()
                    else:
                        exif = None
                    
                    if exif and 274 in exif:  # Orientation tag
                        orientation = exif[274]
                        orientation_names = {
                            1: 'Horizontal (normal)',
                            2: 'Mirrored horizontal',
                            3: 'Rotated 180°',
                            4: 'Mirrored vertical',
                            5: 'Mirrored horizontal then rotated 90° CCW',
                            6: 'Rotated 90° CW',
                            7: 'Mirrored horizontal then rotated 90° CW',
                            8: 'Rotated 90° CCW'
                        }
                        metadata.append(self._format_metadata('Orientation', 
                                            orientation_names.get(orientation, f'Unknown ({orientation})')))
                except:
                    pass
                    
        except Exception as e:
            print(f"Error extracting technical info: {e}")
        return metadata
    
    def _format_exif_value(self, tag_name: str, value) -> str:
        """Форматирует значения EXIF для лучшей читаемости"""
        try:
            # GPS координаты
            if 'gps' in tag_name.lower() and isinstance(value, tuple):
                if 'latitude' in tag_name.lower():
                    return f"{self._convert_gps_coordinate(value)} N"
                elif 'longitude' in tag_name.lower():
                    return f"{self._convert_gps_coordinate(value)} E"
            
            # Даты и время
            if 'date' in tag_name.lower() or 'time' in tag_name.lower():
                if isinstance(value, str) and ':' in value:
                    return value.replace(':', '-', 2)  # Форматируем дату
                    
            # Числовые значения
            if isinstance(value, (int, float)):
                if 'focal' in tag_name.lower():
                    return f"{value}mm"
                elif 'aperture' in tag_name.lower():
                    return f"f/{value}"
                elif 'exposure' in tag_name.lower() and value < 1:
                    return f"1/{int(1/value)}s"
                    
        except:
            pass
            
        return str(value)
    
    def _convert_gps_coordinate(self, coord_tuple) -> str:
        """Конвертирует GPS координаты из tuple в градусы"""
        try:
            degrees, minutes, seconds = coord_tuple
            decimal = degrees + minutes/60 + seconds/3600
            return f"{decimal:.6f}°"
        except:
            return str(coord_tuple)
    
    def _format_gps_value(self, tag: str, value: str) -> str:
        """Форматирует GPS значения"""
        if 'GPSLatitude' in tag:
            return f"{value} (Latitude)"
        elif 'GPSLongitude' in tag:
            return f"{value} (Longitude)"
        elif 'GPSAltitude' in tag:
            return f"{value} meters"
        return value
