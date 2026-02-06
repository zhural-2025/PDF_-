# Инструкция по установке для Windows

## Системные требования

WeasyPrint на Windows требует установки GTK3. Ниже приведены несколько способов установки.

## Способ 1: Установщик GTK3 (Рекомендуется)

1. **Скачайте установщик GTK3:**
   - Перейдите на: https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases
   - Скачайте последнюю версию `gtk3-runtime-*.exe`

2. **Установите GTK3:**
   - Запустите установщик
   - Следуйте инструкциям установщика
   - По умолчанию GTK3 устанавливается в `C:\Program Files\GTK3-Runtime Win64\`

3. **Добавьте GTK3 в PATH:**
   
   **Вариант А: Через графический интерфейс (рекомендуется)**
   - Нажмите `Win + R`, введите `sysdm.cpl` и нажмите Enter
   - Перейдите на вкладку "Дополнительно"
   - Нажмите "Переменные среды" (Environment Variables)
   - В разделе "Системные переменные" найдите `Path` и нажмите "Изменить"
   - Нажмите "Создать" и добавьте путь к `bin` директории GTK3:
     ```
     C:\Program Files\GTK3-Runtime Win64\bin
     ```
     (или путь, куда вы установили GTK3)
   - Нажмите "OK" во всех окнах
   - **ВАЖНО: Перезапустите терминал/IDE полностью**
   
   **Вариант Б: Через командную строку (PowerShell от администратора)**
   ```powershell
   # Найдите путь установки GTK3 (обычно):
   $gtkPath = "C:\Program Files\GTK3-Runtime Win64\bin"
   
   # Добавьте в системный PATH:
   [Environment]::SetEnvironmentVariable(
       "Path",
       [Environment]::GetEnvironmentVariable("Path", "Machine") + ";$gtkPath",
       "Machine"
   )
   ```
   - Перезапустите терминал

4. **Проверьте установку:**
   
   Запустите скрипт проверки:
   ```bash
   python check_installation.py
   ```
   
   Или проверьте вручную:
   ```bash
   python -c "from weasyprint import HTML; print('✓ GTK3 установлен корректно!')"
   ```

## Способ 2: MSYS2

1. **Установите MSYS2:**
   - Скачайте с https://www.msys2.org/
   - Установите в `C:\msys64\` (или другую директорию)

2. **Установите GTK3 через pacman:**
   ```bash
   # Откройте MSYS2 MinGW 64-bit terminal
   pacman -Syu
   pacman -S mingw-w64-x86_64-gtk3
   ```

3. **Добавьте MSYS2 в PATH:**
   - Добавьте `C:\msys64\mingw64\bin` в системную переменную PATH
   - Перезапустите терминал

## Способ 3: Conda (если используете Anaconda/Miniconda)

```bash
conda install -c conda-forge gtk3
pip install -r requirements.txt
```

## Проверка установки

После установки GTK3 и Python-зависимостей проверьте работу:

```bash
python -c "from weasyprint import HTML, CSS; print('✓ WeasyPrint готов к работе!')"
```

Если команда выполняется без ошибок, можно запускать скрипт:

```bash
python pdf_checkmaker.py
```

## Решение проблем

### Ошибка: "Failed to load the libgobject library"

**Решение:**
1. Убедитесь, что GTK3 установлен
2. Проверьте, что путь к GTK3 добавлен в PATH
3. Перезапустите терминал/IDE
4. Убедитесь, что используете правильную версию Python (64-bit)

### Ошибка: "DLL load failed"

**Решение:**
1. Установите Visual C++ Redistributable: https://aka.ms/vs/17/release/vc_redist.x64.exe
2. Переустановите GTK3
3. Проверьте совместимость версий (64-bit Python требует 64-bit GTK3)

### Альтернатива: Docker

Если установка GTK3 вызывает проблемы, используйте Docker:

```bash
# Создайте Dockerfile
docker run -it -v "%cd%":/app -w /app python:3.11 bash
pip install -r requirements.txt
python pdf_checkmaker.py
```
