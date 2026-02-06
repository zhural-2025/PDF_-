# PDF Checkmaker - Генератор PDF-чеков

Python-скрипт для генерации PDF-чеков из CSV/JSON данных и HTML-шаблонов.

> 💡 **Вопросы о WeasyPrint и GTK3?** См. [ABOUT_WEASYPRINT.md](ABOUT_WEASYPRINT.md) для подробного объяснения.

## Установка

### Windows

1. **Установите GTK3 для Windows:**
   - Скачайте установщик GTK3: https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases
   - Запустите установщик и следуйте инструкциям
   - **ВАЖНО:** После установки добавьте путь к GTK3/bin в переменную PATH
   - 📖 **Подробная инструкция:** см. `SETUP_GUIDE.md` или `INSTALL_WINDOWS.md`

2. **Установите Python-зависимости:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Проверьте установку:**
   ```bash
   python check_installation.py
   ```

### macOS

1. **Установите системные зависимости через Homebrew:**
   ```bash
   brew install cairo pango gdk-pixbuf libffi
   ```

2. **Установите Python-зависимости:**
   ```bash
   pip install -r requirements.txt
   ```

### Linux (Ubuntu/Debian)

1. **Установите системные зависимости:**
   ```bash
   sudo apt-get install python3-dev python3-pip python3-cffi \
       libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 \
       libffi-dev shared-mime-info
   ```

2. **Установите Python-зависимости:**
   ```bash
   pip install -r requirements.txt
   ```

## Структура проекта

```
PDF_чекмейкер/
├── pdf_checkmaker.py    # Основной скрипт
├── requirements.txt     # Зависимости
├── data/               # CSV и JSON файлы с данными
├── templates/          # HTML-шаблоны
└── output/             # Сгенерированные PDF файлы
```

## Использование

1. Поместите файлы с данными (CSV или JSON) в директорию `data/`
2. Поместите HTML-шаблоны в директорию `templates/`
3. Запустите скрипт:
```bash
python pdf_checkmaker.py
```

## Формат данных

### CSV файлы
Должны содержать колонки, включая поле для идентификации чека:
- `invoice_id` (или `invoiceId`, `invoice`, `id`, `ID`)

### JSON файлы
Должны быть массивом объектов или одним объектом:
```json
[
  {
    "invoice_id": "INV-001",
    "date": "2024-01-15",
    "customer_name": "Иван Петров",
    "amount": "1500.00",
    ...
  }
]
```

## HTML-шаблоны

В шаблонах используйте фигурные скобки для подстановки данных:
- `{{field_name}}` или `{field_name}`

Пример:
```html
<h1>Чек {{invoice_id}}</h1>
<p>Клиент: {{customer_name}}</p>
```

## Особенности

- ✅ Поддержка кириллицы (DejaVu Sans)
- ✅ Работа на Windows и macOS
- ✅ Автоматическое открытие PDF после генерации
- ✅ Удобное консольное меню

## Устранение проблем

### Windows: Ошибка "Failed to load the libgobject library"

Если при запуске возникает ошибка о загрузке библиотек GTK3:

1. Убедитесь, что GTK3 установлен и добавлен в PATH
2. Перезапустите терминал после установки GTK3
3. Проверьте установку:
   ```bash
   python -c "from weasyprint import HTML; print('WeasyPrint работает!')"
   ```

### Альтернатива для Windows

Если установка GTK3 вызывает проблемы, можно использовать Docker:
```bash
docker run -v "%cd%":/app -w /app python:3.11 python pdf_checkmaker.py
```
