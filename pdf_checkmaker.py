#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PDF Checkmaker - Генератор PDF-чеков из CSV/JSON данных и HTML-шаблонов
"""

import os
import json
import sys
import platform
import subprocess
import io
from pathlib import Path
from typing import Dict, List, Any, Optional

# Настройка кодировки для Windows консоли
if sys.platform == 'win32':
    try:
        if hasattr(sys.stdout, 'buffer'):
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        if hasattr(sys.stderr, 'buffer'):
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
        os.environ['PYTHONIOENCODING'] = 'utf-8'
    except:
        pass

try:
    import pandas as pd
except ImportError:
    print("Ошибка: pandas не установлен. Установите его: pip install pandas")
    sys.exit(1)

try:
    from weasyprint import HTML, CSS
except ImportError:
    print("Ошибка: weasyprint не установлен. Установите его: pip install weasyprint")
    sys.exit(1)
except Exception as e:
    error_msg = str(e).lower()
    if "gobject" in error_msg or "gtk" in error_msg or "dll" in error_msg:
        print("="*60)
        print("ОШИБКА: Не удалось загрузить GTK3")
        print("="*60)
        print("\nWeasyPrint требует установки GTK3 на Windows.")
        print("\nИнструкции по установке:")
        print("1. См. файл INSTALL_WINDOWS.md")
        print("2. Или установите GTK3 с:")
        print("   https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases")
        print("\nПосле установки GTK3:")
        print("- Добавьте путь к GTK3/bin в переменную PATH")
        print("- Перезапустите терминал")
        print("="*60)
    else:
        print(f"Ошибка при импорте WeasyPrint: {e}")
        print("Проверьте установку: pip install weasyprint")
    sys.exit(1)


class PDFCheckmaker:
    """Класс для генерации PDF-чеков из данных и шаблонов"""
    
    def __init__(self, data_dir: str = "data", templates_dir: str = "templates", output_dir: str = "output"):
        self.data_dir = Path(data_dir)
        self.templates_dir = Path(templates_dir)
        self.output_dir = Path(output_dir)
        
        # Создаем директории, если их нет
        self.data_dir.mkdir(exist_ok=True)
        self.templates_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
    
    def get_data_files(self) -> List[Path]:
        """Получить список всех CSV и JSON файлов в директории data"""
        data_files = []
        if self.data_dir.exists():
            data_files.extend(self.data_dir.glob("*.csv"))
            data_files.extend(self.data_dir.glob("*.json"))
        return sorted(data_files)
    
    def get_template_files(self) -> List[Path]:
        """Получить список всех HTML файлов в директории templates"""
        template_files = []
        if self.templates_dir.exists():
            template_files.extend(self.templates_dir.glob("*.html"))
        return sorted(template_files)
    
    def load_csv_data(self, file_path: Path) -> List[Dict[str, Any]]:
        """Загрузить данные из CSV файла"""
        try:
            # Используем str() для Path, чтобы избежать проблем с кодировкой на Windows
            df = pd.read_csv(str(file_path), encoding='utf-8')
            # Конвертируем DataFrame в список словарей
            return df.to_dict('records')
        except Exception as e:
            print(f"Ошибка при чтении CSV файла: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def load_json_data(self, file_path: Path) -> List[Dict[str, Any]]:
        """Загрузить данные из JSON файла"""
        try:
            # Используем str() для Path, чтобы избежать проблем с кодировкой на Windows
            with open(str(file_path), 'r', encoding='utf-8') as f:
                data = json.load(f)
            # Если данные - список, возвращаем как есть
            if isinstance(data, list):
                return data
            # Если данные - словарь, оборачиваем в список
            elif isinstance(data, dict):
                return [data]
            else:
                print("Неожиданный формат JSON данных")
                return []
        except Exception as e:
            print(f"Ошибка при чтении JSON файла: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def load_data(self, file_path: Path) -> List[Dict[str, Any]]:
        """Загрузить данные из файла (CSV или JSON)"""
        if file_path.suffix.lower() == '.csv':
            return self.load_csv_data(file_path)
        elif file_path.suffix.lower() == '.json':
            return self.load_json_data(file_path)
        else:
            return []
    
    def get_invoice_ids(self, data: List[Dict[str, Any]]) -> List[str]:
        """Извлечь список invoice_id из данных"""
        invoice_ids = []
        for record in data:
            # Пробуем разные варианты названий поля
            invoice_id = (
                record.get('invoice_id') or 
                record.get('invoiceId') or 
                record.get('invoice') or
                record.get('id') or
                record.get('ID')
            )
            if invoice_id:
                invoice_ids.append(str(invoice_id))
        return sorted(list(set(invoice_ids)))  # Убираем дубликаты и сортируем
    
    def get_record_by_invoice_id(self, data: List[Dict[str, Any]], invoice_id: str) -> Optional[Dict[str, Any]]:
        """Найти запись по invoice_id"""
        for record in data:
            invoice_id_field = (
                record.get('invoice_id') or 
                record.get('invoiceId') or 
                record.get('invoice') or
                record.get('id') or
                record.get('ID')
            )
            if str(invoice_id_field) == str(invoice_id):
                return record
        return None
    
    def load_template(self, template_path: Path) -> str:
        """Загрузить HTML-шаблон"""
        try:
            # Используем str() для Path, чтобы избежать проблем с кодировкой на Windows
            with open(str(template_path), 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Ошибка при чтении шаблона: {e}")
            import traceback
            traceback.print_exc()
            return ""
    
    def render_template(self, template: str, data: Dict[str, Any]) -> str:
        """Подставить данные в HTML-шаблон"""
        html = template
        # Простая подстановка через форматирование строк
        # Поддерживаем как {field_name}, так и {{field_name}}
        # Важно: сначала заменяем {{key}}, потом {key}, чтобы избежать конфликтов
        for key, value in data.items():
            value_str = str(value) if value is not None else ""
            # Заменяем {{key}} (двойные фигурные скобки) - сначала!
            html = html.replace(f"{{{{{key}}}}}", value_str)
            # Заменяем {key} (одинарные фигурные скобки) - потом
            html = html.replace(f"{{{key}}}", value_str)
        return html
    
    def generate_pdf(self, html_content: str, output_path: Path):
        """Сгенерировать PDF из HTML с поддержкой кириллицы"""
        try:
            # WeasyPrint по умолчанию использует DejaVu Sans, который поддерживает кириллицу
            # Добавляем CSS для явного указания шрифта
            css = CSS(string='''
                @page {
                    size: A4;
                    margin: 2cm;
                }
                body {
                    font-family: 'DejaVu Sans', 'Liberation Sans', Arial, sans-serif;
                }
            ''')
            
            # Генерируем PDF
            # Используем str() для Path, чтобы избежать проблем с кодировкой на Windows
            # В новых версиях WeasyPrint параметр encoding не нужен - кодировка определяется автоматически
            HTML(string=html_content).write_pdf(
                str(output_path),
                stylesheets=[css]
            )
            print(f"[OK] PDF успешно создан: {output_path}")
        except Exception as e:
            print(f"Ошибка при генерации PDF: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def open_pdf(self, pdf_path: Path):
        """Открыть PDF в системной программе"""
        try:
            system = platform.system()
            if system == 'Windows':
                os.startfile(str(pdf_path))
            elif system == 'Darwin':  # macOS
                subprocess.run(['open', str(pdf_path)])
            elif system == 'Linux':
                subprocess.run(['xdg-open', str(pdf_path)])
            else:
                print(f"Неизвестная ОС: {system}. Откройте PDF вручную: {pdf_path}")
        except Exception as e:
            print(f"Не удалось открыть PDF автоматически: {e}")
            print(f"Откройте файл вручную: {pdf_path}")
    
    def display_menu(self, title: str, items: List[Any], item_name: str = "элемент") -> Optional[int]:
        """Отобразить меню и получить выбор пользователя"""
        if not items:
            print(f"\n[!] Нет доступных {item_name}ов")
            return None
        
        print(f"\n{'='*50}")
        print(f"  {title}")
        print(f"{'='*50}")
        for i, item in enumerate(items, 1):
            print(f"  {i}. {item}")
        print(f"{'='*50}")
        
        while True:
            try:
                choice = input(f"\nВыберите {item_name} (1-{len(items)}): ").strip()
                index = int(choice) - 1
                if 0 <= index < len(items):
                    return index
                else:
                    print(f"[!] Пожалуйста, введите число от 1 до {len(items)}")
            except ValueError:
                print("[!] Пожалуйста, введите число")
            except KeyboardInterrupt:
                print("\n\nОперация отменена пользователем")
                return None
    
    def run(self):
        """Основной цикл программы"""
        print("\n" + "="*50)
        print("  PDF CHECKMAKER - Генератор PDF-чеков")
        print("="*50)
        
        # Получаем списки файлов
        data_files = self.get_data_files()
        template_files = self.get_template_files()
        
        # Выводим доступные файлы
        print("\n[ФАЙЛЫ] Доступные файлы с данными:")
        if data_files:
            for i, file in enumerate(data_files, 1):
                print(f"   {i}. {file.name}")
        else:
            print("   (нет файлов)")
        
        print("\n[ШАБЛОНЫ] Доступные HTML-шаблоны:")
        if template_files:
            for i, template in enumerate(template_files, 1):
                print(f"   {i}. {template.name}")
        else:
            print("   (нет шаблонов)")
        
        if not data_files or not template_files:
            print("\n[!] Для работы программы нужны хотя бы один файл данных и один шаблон")
            return
        
        # Выбор файла данных
        data_index = self.display_menu(
            "Выбор файла с данными",
            [f.name for f in data_files],
            "файл"
        )
        if data_index is None:
            return
        
        selected_data_file = data_files[data_index]
        print(f"\n[OK] Выбран файл: {selected_data_file.name}")
        
        # Загружаем данные
        data = self.load_data(selected_data_file)
        if not data:
            print("[!] Не удалось загрузить данные из файла")
            return
        
        # Выбор шаблона
        template_index = self.display_menu(
            "Выбор HTML-шаблона",
            [f.name for f in template_files],
            "шаблон"
        )
        if template_index is None:
            return
        
        selected_template = template_files[template_index]
        print(f"\n[OK] Выбран шаблон: {selected_template.name}")
        
        # Загружаем шаблон
        template_content = self.load_template(selected_template)
        if not template_content:
            print("[!] Не удалось загрузить шаблон")
            return
        
        # Получаем список invoice_id
        invoice_ids = self.get_invoice_ids(data)
        if not invoice_ids:
            print("\n[!] В данных не найдено поле invoice_id (или invoiceId, invoice, id, ID)")
            print("Доступные поля в первой записи:")
            if data:
                for key in data[0].keys():
                    print(f"   - {key}")
            return
        
        # Выбор invoice_id
        invoice_index = self.display_menu(
            "Выбор чека (по invoice_id)",
            invoice_ids,
            "чек"
        )
        if invoice_index is None:
            return
        
        selected_invoice_id = invoice_ids[invoice_index]
        print(f"\n[OK] Выбран чек: {selected_invoice_id}")
        
        # Находим запись
        record = self.get_record_by_invoice_id(data, selected_invoice_id)
        if not record:
            print("[!] Не удалось найти запись с указанным invoice_id")
            return
        
        # Генерируем HTML
        html_content = self.render_template(template_content, record)
        
        # Генерируем PDF
        output_filename = f"check_{selected_invoice_id}.pdf"
        output_path = self.output_dir / output_filename
        
        try:
            self.generate_pdf(html_content, output_path)
            
            # Открываем PDF
            print("\n[ОТКРЫВАЮ] Открываю PDF...")
            self.open_pdf(output_path)
            
            print("\n[OK] Готово!")
            
        except Exception as e:
            print(f"\n[ОШИБКА] Ошибка при генерации PDF: {e}")


def main():
    """Точка входа в программу"""
    try:
        checkmaker = PDFCheckmaker()
        checkmaker.run()
    except KeyboardInterrupt:
        print("\n\nОперация отменена пользователем")
    except Exception as e:
        print(f"\n[ОШИБКА] Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
