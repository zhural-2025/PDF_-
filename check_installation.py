#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Скрипт для проверки установки зависимостей PDF Checkmaker
"""

import sys
import os
import platform
import io

# Настройка кодировки для Windows консоли
if sys.platform == 'win32':
    try:
        # Пытаемся установить UTF-8 для консоли
        if hasattr(sys.stdout, 'buffer'):
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        if hasattr(sys.stderr, 'buffer'):
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
        # Альтернатива: установить переменную окружения
        os.environ['PYTHONIOENCODING'] = 'utf-8'
    except:
        pass

# ASCII-совместимые символы для консоли
OK = "[OK]"
FAIL = "[FAIL]"
WARN = "[!]"

def check_python_version():
    """Проверка версии Python"""
    print("="*60)
    print("Проверка версии Python")
    print("="*60)
    version = sys.version_info
    print(f"Python {version.major}.{version.minor}.{version.micro}")
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"{WARN} Предупреждение: Рекомендуется Python 3.8+")
    else:
        print(f"{OK} Версия Python подходит")
    print()

def check_python_packages():
    """Проверка установленных Python-пакетов"""
    print("="*60)
    print("Проверка Python-пакетов")
    print("="*60)
    
    packages = {
        'pandas': 'pandas',
        'weasyprint': 'weasyprint'
    }
    
    missing = []
    for package_name, import_name in packages.items():
        try:
            __import__(import_name)
            print(f"{OK} {package_name} установлен")
        except ImportError:
            print(f"{FAIL} {package_name} НЕ установлен")
            missing.append(package_name)
    
    if missing:
        print(f"\n{WARN} Установите недостающие пакеты: pip install {' '.join(missing)}")
    else:
        print(f"\n{OK} Все Python-пакеты установлены")
    print()
    return len(missing) == 0

def check_gtk3_windows():
    """Проверка GTK3 на Windows"""
    print("="*60)
    print("Проверка GTK3 (Windows)")
    print("="*60)
    
    if platform.system() != 'Windows':
        print("Проверка GTK3 актуальна только для Windows")
        print()
        return True
    
    # Проверяем стандартные пути установки GTK3
    common_paths = [
        r"C:\Program Files\GTK3-Runtime Win64\bin",
        r"C:\Program Files (x86)\GTK3-Runtime Win64\bin",
        r"C:\msys64\mingw64\bin",
        r"C:\msys64\usr\bin",
    ]
    
    # Проверяем PATH
    path_env = os.environ.get('PATH', '').lower()
    gtk_found_in_path = False
    
    for path in common_paths:
        if os.path.exists(path):
            print(f"{OK} Найден GTK3: {path}")
            if path.lower() in path_env:
                print(f"  {OK} Путь добавлен в PATH")
                gtk_found_in_path = True
            else:
                print(f"  {WARN} Путь НЕ в PATH - добавьте его вручную")
    
    # Проверяем наличие DLL файлов
    dll_files = ['libgobject-2.0-0.dll', 'libgtk-3-0.dll', 'libcairo-2.dll']
    found_dlls = []
    
    for path in common_paths:
        if os.path.exists(path):
            for dll in dll_files:
                dll_path = os.path.join(path, dll)
                if os.path.exists(dll_path):
                    found_dlls.append(dll)
    
    if found_dlls:
        print(f"\n{OK} Найдены DLL файлы: {', '.join(set(found_dlls))}")
    else:
        print(f"\n{WARN} DLL файлы GTK3 не найдены в стандартных путях")
    
    print()
    return gtk_found_in_path or len(found_dlls) > 0

def test_weasyprint():
    """Тест импорта и работы WeasyPrint"""
    print("="*60)
    print("Тест WeasyPrint")
    print("="*60)
    
    try:
        from weasyprint import HTML, CSS
        print(f"{OK} WeasyPrint импортирован успешно")
        
        # Пробуем создать простой PDF
        try:
            html_content = """
            <html>
                <body>
                    <h1>Тест</h1>
                    <p>Проверка работы WeasyPrint</p>
                </body>
            </html>
            """
            css = CSS(string='body { font-family: Arial; }')
            
            # Создаем тестовый PDF в памяти (не сохраняем)
            test_pdf = HTML(string=html_content).write_pdf(stylesheets=[css])
            
            if test_pdf:
                print(f"{OK} WeasyPrint успешно создал тестовый PDF")
                print(f"{OK} GTK3 работает корректно!")
                return True
        except Exception as e:
            error_msg = str(e).lower()
            if "gobject" in error_msg or "gtk" in error_msg or "dll" in error_msg:
                print(f"{FAIL} Ошибка: GTK3 не загружен")
                print(f"  Детали: {e}")
                print("\nРешение:")
                print("1. Убедитесь, что GTK3 установлен")
                print("2. Добавьте путь к GTK3/bin в переменную PATH")
                print("3. Перезапустите терминал")
                return False
            else:
                print(f"{WARN} Предупреждение при создании PDF: {e}")
                return False
                
    except ImportError:
        print(f"{FAIL} WeasyPrint не установлен")
        print("  Установите: pip install weasyprint")
        return False
    except Exception as e:
        error_msg = str(e).lower()
        if "gobject" in error_msg or "gtk" in error_msg:
            print(f"{FAIL} Ошибка загрузки GTK3")
            print(f"  {e}")
            print("\nРешение:")
            print("1. Установите GTK3 с https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases")
            print("2. Добавьте путь к GTK3/bin в PATH")
            print("3. Перезапустите терминал")
        else:
            print(f"{FAIL} Неожиданная ошибка: {e}")
        return False
    
    print()
    return False

def main():
    """Основная функция проверки"""
    print("\n" + "="*60)
    print("  ПРОВЕРКА УСТАНОВКИ PDF CHECKMAKER")
    print("="*60 + "\n")
    
    checks = []
    
    # Проверка Python
    check_python_version()
    
    # Проверка пакетов
    checks.append(("Python-пакеты", check_python_packages()))
    
    # Проверка GTK3 (только Windows)
    if platform.system() == 'Windows':
        checks.append(("GTK3", check_gtk3_windows()))
    
    # Тест WeasyPrint
    checks.append(("WeasyPrint", test_weasyprint()))
    
    # Итоги
    print("="*60)
    print("ИТОГИ ПРОВЕРКИ")
    print("="*60)
    
    all_ok = True
    for name, status in checks:
        status_icon = OK if status else FAIL
        print(f"{status_icon} {name}: {'OK' if status else 'ТРЕБУЕТСЯ УСТАНОВКА'}")
        if not status:
            all_ok = False
    
    print()
    if all_ok:
        print("="*60)
        print(f"{OK} ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ!")
        print("  Можно запускать: python pdf_checkmaker.py")
        print("="*60)
    else:
        print("="*60)
        print(f"{WARN} ТРЕБУЮТСЯ ДОПОЛНИТЕЛЬНЫЕ ДЕЙСТВИЯ")
        print("  См. инструкции в INSTALL_WINDOWS.md")
        print("="*60)
    
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nПроверка прервана пользователем")
    except Exception as e:
        print(f"\n{FAIL} Ошибка при проверке: {e}")
        import traceback
        traceback.print_exc()
