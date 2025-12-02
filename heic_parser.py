from typing import List, Dict
from .base_parser import BaseParser
import os
from pathlib import Path
from datetime import datetime
from PIL import Image

class HEICParser(BaseParser):
    
    @staticmethod
    def supported_formats() -> List[str]:
        return [
            'image/heic',
            'image/heif'
        ]
        
    def extract_metadata(self, file_path: str) -> List[Dict]:
        metadata = []
        
        try:
            # Всегда извлекаем базовую информацию о файле
            file_info = self._get_file_info(file_path)
            for key, value in file_info.items():
                metadata.append(self._format_metadata(key, value))
            
            # Пытаемся использовать pillow-heif если доступен
            if self._has_pillow_heif():
                heif_metadata = self._extract_with_pillow_heif(file_path)
                metadata.extend(heif_metadata)
            else:
                metadata.append(self._format_metadata('HEIC_Warning', 
                    'pillow-heif not available. Install with: pip install pillow-heif'))
                
        except Exception as e:
            print(f"Error reading HEIC metadata: {e}")
            # Возвращаем только базовую информацию в случае ошибки
            file_info = self._get_file_info(file_path)
            for key, value in file_info.items():
                metadata.append(self._format_metadata(key, value))
            
        return metadata
    
    def _has_pillow_heif(self) -> bool:
        """Проверяет, доступен ли pillow-heif"""
        try:
            import pillow_heif
            return True
        except ImportError:
            return False
    
    def _extract_with_pillow_heif(self, file_path: str) -> List[Dict]:
        """Извлекает метаданные через pillow-heif"""
        metadata = []
        
        try:
            import pillow_heif
            from PIL import Image, ExifTags
            
            # Регистрируем HEIF opener
            pillow_heif.register_heif_opener()
            
            # Открываем изображение
            with Image.open(file_path) as img:
                # EXIF данные
                exif_metadata = self._extract_exif_data(img)
                metadata.extend(exif_metadata)
                
                # Информация о изображении
                image_metadata = self._extract_image_info(img, file_path)
                metadata.extend(image_metadata)
                
                # Техническая информация
                tech_metadata = self._extract_technical_info(img)
                metadata.extend(tech_metadata)
                
                # Дополнительные метаданные
                additional_metadata = self._extract_additional_metadata(img)
                metadata.extend(additional_metadata)
                        
        except Exception as e:
            print(f"Error with pillow-heif extraction: {e}")
            
        return metadata
    
    def _extract_exif_data(self, img: Image.Image) -> List[Dict]:
        """Извлекает EXIF данные"""
        metadata = []
        try:
            # Используем getexif() если доступно, иначе _getexif()
            if hasattr(img, 'getexif'):
                exif_data = img.getexif()
            elif hasattr(img, '_getexif'):
                exif_data = img._getexif()
            else:
                exif_data = None
            
            if exif_data:
                for tag_id, value in exif_data.items():
                    tag_name = self._get_exif_tag_name(tag_id)
                    if value:
                        formatted_value = self._format_exif_value(tag_name, value)
                        metadata.append(self._format_metadata(f'EXIF_{tag_name}', formatted_value))
        except Exception as e:
            print(f"Error extracting EXIF: {e}")
        return metadata
    
    def _extract_image_info(self, img: Image.Image, file_path: str) -> List[Dict]:
        """Извлекает информацию о изображении"""
        metadata = []
        try:
            image_info = {
                'Image Width': img.width,
                'Image Height': img.height,
                'Image Mode': img.mode,
                'Image Format': img.format,
                'Image Bands': ', '.join(img.getbands()) if hasattr(img, 'getbands') else 'N/A',
                'Image Palette': 'Yes' if img.palette else 'No',
                'Image Animated': 'Yes' if getattr(img, 'is_animated', False) else 'No',
                'Image Frames': getattr(img, 'n_frames', 1),
                'Aspect Ratio': f"{img.width}:{img.height}",
                'Megapixels': f"{(img.width * img.height) / 1000000:.2f} MP",
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
    
    def _extract_technical_info(self, img: Image.Image) -> List[Dict]:
        """Извлекает техническую информацию"""
        metadata = []
        try:
            # Информация о сжатии и настройках
            if hasattr(img, 'info'):
                for key, value in img.info.items():
                    if key not in ('icc_profile', 'exif'):  # Исключаем уже обработанные
                        if key == 'dpi':
                            if isinstance(value, tuple) and len(value) == 2:
                                metadata.append(self._format_metadata('Resolution', f'{value[0]}x{value[1]} DPI'))
                            else:
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
    
    def _extract_additional_metadata(self, img: Image.Image) -> List[Dict]:
        """Извлекает дополнительную информацию"""
        metadata = []
        try:
            # Попробуем получить информацию о камере из EXIF
            # Используем getexif() если доступно, иначе _getexif()
            if hasattr(img, 'getexif'):
                exif = img.getexif()
            elif hasattr(img, '_getexif'):
                exif = img._getexif()
            else:
                exif = None
            
            if exif:
                camera_info = {}
                
                # Производитель камеры
                if 271 in exif and exif[271]:
                    camera_info['Camera Make'] = exif[271]
                
                # Модель камеры
                if 272 in exif and exif[272]:
                    camera_info['Camera Model'] = exif[272]
                
                # Настройки съемки
                shooting_info = {}
                if 33434 in exif:  # ExposureTime
                    shooting_info['Exposure Time'] = f"{exif[33434]}s"
                if 33437 in exif:  # FNumber
                    shooting_info['Aperture'] = f"f/{exif[33437]}"
                if 34855 in exif:  # ISOSpeedRatings
                    shooting_info['ISO'] = exif[34855]
                if 37386 in exif:  # FocalLength
                    shooting_info['Focal Length'] = f"{exif[37386]}mm"
                
                # Добавляем информацию о камере
                for key, value in camera_info.items():
                    metadata.append(self._format_metadata(key, value))
                
                # Добавляем настройки съемки
                for key, value in shooting_info.items():
                    metadata.append(self._format_metadata(key, value))
                    
        except Exception as e:
            print(f"Error extracting additional metadata: {e}")
        return metadata
    
    def _get_file_info(self, file_path: str) -> Dict[str, str]:
        """Извлекает базовую информацию о файле"""
        try:
            stat = os.stat(file_path)
            file_size = stat.st_size
            size_kb = file_size / 1024
            size_mb = size_kb / 1024
            
            size_str = f"{file_size} bytes"
            if size_mb >= 1:
                size_str = f"{size_mb:.1f} MB"
            elif size_kb >= 1:
                size_str = f"{size_kb:.1f} KB"
            
            return {
                'File Name': os.path.basename(file_path),
                'File Size': size_str,
                'File Extension': Path(file_path).suffix.upper(),
                'File Path': file_path,
                'File Created': datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S'),
                'File Modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                'File Accessed': datetime.fromtimestamp(stat.st_atime).strftime('%Y-%m-%d %H:%M:%S'),
                'File Format': 'HEIC/HEIF',
            }
        except Exception as e:
            return {'Error': f'Failed to extract file info: {e}'}
    
    def _format_exif_value(self, tag_name: str, value) -> str:
        """Форматирует значения EXIF для лучшей читаемости"""
        try:
            # GPS координаты
            if 'gps' in tag_name.lower() and isinstance(value, tuple):
                if 'latitude' in tag_name.lower():
                    return f"{self._convert_gps_coordinate(value)} N"
                elif 'longitude' in tag_name.lower():
                    return f"{self._convert_gps_coordinate(value)} E"
                elif 'altitude' in tag_name.lower():
                    return f"{value} meters"
            
            # Даты и время
            if 'date' in tag_name.lower() or 'time' in tag_name.lower():
                if isinstance(value, str) and ':' in value:
                    return value.replace(':', '-', 2)
                    
            # Числовые значения
            if isinstance(value, (int, float)):
                if 'focal' in tag_name.lower():
                    return f"{value}mm"
                elif 'aperture' in tag_name.lower() or 'fnumber' in tag_name.lower():
                    return f"f/{value}"
                elif 'exposure' in tag_name.lower() and isinstance(value, float) and value < 1:
                    return f"1/{int(1/value)}s"
                elif 'iso' in tag_name.lower():
                    return f"ISO {value}"
                    
        except:
            pass
            
        return str(value)
    
    def _convert_gps_coordinate(self, coord_tuple) -> str:
        """Конвертирует GPS координаты из tuple в градусы"""
        try:
            if isinstance(coord_tuple, tuple) and len(coord_tuple) == 3:
                degrees, minutes, seconds = coord_tuple
                decimal = degrees + minutes/60 + seconds/3600
                return f"{decimal:.6f}°"
        except:
            pass
        return str(coord_tuple)
    
    def _get_exif_tag_name(self, tag_id: int) -> str:
        """Преобразует ID EXIF тега в читаемое имя"""
        exif_tags = {
            # Основные теги
            271: 'Make',
            272: 'Model',
            274: 'Orientation',
            282: 'XResolution',
            283: 'YResolution',
            296: 'ResolutionUnit',
            305: 'Software',
            306: 'DateTime',
            315: 'Artist',
            33432: 'Copyright',
            
            # EXIF теги
            36864: 'ExifVersion',
            36867: 'DateTimeOriginal',
            36868: 'DateTimeDigitized',
            37377: 'ShutterSpeedValue',
            37378: 'ApertureValue',
            37379: 'BrightnessValue',
            37380: 'ExposureBiasValue',
            37381: 'MaxApertureValue',
            37382: 'SubjectDistance',
            37383: 'MeteringMode',
            37384: 'LightSource',
            37385: 'Flash',
            37386: 'FocalLength',
            37387: 'FlashEnergy',
            37388: 'SpatialFrequencyResponse',
            37389: 'Noise',
            37390: 'FocalPlaneXResolution',
            37391: 'FocalPlaneYResolution',
            37392: 'FocalPlaneResolutionUnit',
            37393: 'ImageNumber',
            37394: 'SecurityClassification',
            37395: 'ImageHistory',
            37396: 'SubjectArea',
            37397: 'ExposureIndex',
            37398: 'TIFF/EPStandardID',
            37399: 'SensingMethod',
            37500: 'MakerNote',
            37510: 'UserComment',
            
            # GPS теги
            34853: 'GPSInfo',
            0: 'GPSVersionID',
            1: 'GPSLatitudeRef',
            2: 'GPSLatitude',
            3: 'GPSLongitudeRef',
            4: 'GPSLongitude',
            5: 'GPSAltitudeRef',
            6: 'GPSAltitude',
            7: 'GPSTimeStamp',
            8: 'GPSSatellites',
            9: 'GPSStatus',
            10: 'GPSMeasureMode',
            11: 'GPSDOP',
            12: 'GPSSpeedRef',
            13: 'GPSSpeed',
            14: 'GPSTrackRef',
            15: 'GPSTrack',
            16: 'GPSImgDirectionRef',
            17: 'GPSImgDirection',
            18: 'GPSMapDatum',
            19: 'GPSDestLatitudeRef',
            20: 'GPSDestLatitude',
            21: 'GPSDestLongitudeRef',
            22: 'GPSDestLongitude',
            23: 'GPSDestBearingRef',
            24: 'GPSDestBearing',
            25: 'GPSDestDistanceRef',
            26: 'GPSDestDistance',
            27: 'GPSProcessingMethod',
            28: 'GPSAreaInformation',
            29: 'GPSDateStamp',
            30: 'GPSDifferential',
            
            # Дополнительные теги
            33434: 'ExposureTime',
            33437: 'FNumber',
            34850: 'ExposureProgram',
            34855: 'ISOSpeedRatings',
            34856: 'OECF',
            34866: 'SpectralSensitivity',
            37520: 'SubsecTime',
            37521: 'SubsecTimeOriginal',
            37522: 'SubsecTimeDigitized',
            40960: 'FlashPixVersion',
            40961: 'ColorSpace',
            40962: 'PixelXDimension',
            40963: 'PixelYDimension',
            40964: 'RelatedSoundFile',
            41483: 'FlashEnergy',
            41484: 'SpatialFrequencyResponse',
            41486: 'FocalPlaneXResolution',
            41487: 'FocalPlaneYResolution',
            41488: 'FocalPlaneResolutionUnit',
            41492: 'SubjectLocation',
            41493: 'ExposureIndex',
            41495: 'SensingMethod',
            41728: 'FileSource',
            41729: 'SceneType',
            41730: 'CFAPattern',
            41985: 'CustomRendered',
            41986: 'ExposureMode',
            41987: 'WhiteBalance',
            41988: 'DigitalZoomRatio',
            41989: 'FocalLengthIn35mmFilm',
            41990: 'SceneCaptureType',
            41991: 'GainControl',
            41992: 'Contrast',
            41993: 'Saturation',
            41994: 'Sharpness',
            41995: 'DeviceSettingDescription',
            41996: 'SubjectDistanceRange',
            42016: 'ImageUniqueID',
            42032: 'CameraOwnerName',
            42033: 'BodySerialNumber',
            42034: 'LensSpecification',
            42035: 'LensMake',
            42036: 'LensModel',
            42037: 'LensSerialNumber',
        }
        return exif_tags.get(tag_id, f'EXIF_Tag_{tag_id}')
