#!/usr/bin/env python3
"""
Автоматическое распознавание аудиофайлов с помощью Whisper
Скрипт ищет аудиофайлы в текущей директории и создает два типа .md файлов:
1. filename.md - простая дословная расшифровка
2. filename_accurate.md - подробная техническая расшифровка

Использование:
    python audio_transcriber.py                    # использует модель medium (по умолчанию)
    python audio_transcriber.py --model large      # использует модель large
    python audio_transcriber.py --list-models      # показать все доступные модели
"""

import os
import glob
import whisper
import datetime
from pathlib import Path
import json
import argparse
import time
import subprocess
from tqdm import tqdm


def get_audio_files():
    """Получить список всех аудиофайлов в текущей директории"""
    audio_extensions = ['*.mp3', '*.wav', '*.m4a', '*.flac', '*.ogg', '*.wma', '*.aac']
    audio_files = []
    
    for extension in audio_extensions:
        audio_files.extend(glob.glob(extension))
    
    return audio_files


def format_duration(seconds):
    """Форматировать длительность в читаемый вид"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    
    if hours > 0:
        return f"{hours}ч {minutes}м {seconds}с"
    elif minutes > 0:
        return f"{minutes}м {seconds}с"
    else:
        return f"{seconds}с"


def estimate_processing_time(file_size_mb, model_name):
    """Оценить время обработки на основе размера файла и модели"""
        # Коэффициенты на основе эмпирических данных (секунды на МБ)
    model_coefficients = {
        'tiny': 0.1, 'tiny.en': 0.1,
        'base': 0.2, 'base.en': 0.2,
        'small': 0.4, 'small.en': 0.4,
        'medium': 0.8, 'medium.en': 0.8,
        'large-v1': 1.5, 'large-v2': 1.5, 'large-v3': 1.5, 'large': 1.5,
        'turbo': 0.6, 'large-v3-turbo': 0.6
    }
    
    coefficient = model_coefficients.get(model_name, 1.0)
    estimated_seconds = file_size_mb * coefficient
    return max(estimated_seconds, 10)  # Минимум 10 секунд


def send_macos_notification(title, message, subtitle=None):
    """Отправить уведомление macOS"""
    try:
        cmd = ['osascript', '-e', f'display notification "{message}" with title "{title}"']
        if subtitle:
            cmd = ['osascript', '-e', f'display notification "{message}" with title "{title}" subtitle "{subtitle}"']
        subprocess.run(cmd, check=True, capture_output=True)
    except Exception as e:
        print(f"⚠️ Не удалось отправить уведомление: {e}")


def create_smart_filename(base_name, extension, add_timestamp=True):
    """Создать умное имя файла с избежанием конфликтов"""
    if add_timestamp:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{base_name}_{timestamp}{extension}"
    else:
        # Проверяем существование файла и добавляем счетчик при необходимости
        counter = 1
        filename = f"{base_name}{extension}"
        while os.path.exists(filename):
            filename = f"{base_name}_{counter}{extension}"
            counter += 1
        return filename


def create_simple_markdown(audio_file, result):
    """Создать простой markdown файл с дословной расшифровкой"""
    base_name = Path(audio_file).stem
    md_file = create_smart_filename(base_name, ".md", add_timestamp=False)
    
    # Предпросмотр для уведомления (первые 50 символов)
    preview = result['text'].strip()[:50]
    if len(result['text'].strip()) > 50:
        preview += "..."
    
    # Создаем простое содержимое markdown файла
    content = f"""# Транскрипция: {audio_file}

{result['text'].strip()}
"""
    
    # Записываем файл
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return md_file, preview


def create_detailed_markdown(audio_file, result, model_name):
    """Создать подробный markdown файл с детальной информацией"""
    base_name = Path(audio_file).stem
    md_file = create_smart_filename(f"{base_name}_accurate", ".md", add_timestamp=False)
    
    # Получаем информацию о файле
    file_size = os.path.getsize(audio_file)
    file_size_mb = file_size / (1024 * 1024)
    
    # Текущее время
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Создаем детальное содержимое markdown файла
    content = f"""# Детальная транскрипция: {audio_file}

## Информация о файле
- **Имя файла**: `{audio_file}`
- **Размер**: {file_size_mb:.2f} МБ
- **Дата обработки**: {timestamp}
- **Модель Whisper**: {model_name}

## Результаты распознавания

### Основной текст
```
{result['text'].strip()}
```

### Детальная информация
"""

    # Добавляем информацию о языке, если есть
    if 'language' in result:
        content += f"- **Обнаруженный язык**: {result['language']}\n"
    
    # Добавляем сегменты с временными метками, если есть
    if 'segments' in result and result['segments']:
        content += "\n### Временные сегменты\n\n"
        for i, segment in enumerate(result['segments'], 1):
            start_time = format_duration(segment['start'])
            end_time = format_duration(segment['end'])
            text = segment['text'].strip()
            content += f"**{i}. [{start_time} - {end_time}]**\n"
            content += f"```\n{text}\n```\n\n"
    
    # Добавляем дополнительную техническую информацию
    content += f"""
### Техническая информация
- **Общая длительность**: {format_duration(result.get('segments', [{}])[-1].get('end', 0)) if result.get('segments') else 'Неизвестно'}
- **Количество сегментов**: {len(result.get('segments', []))}
- **Средняя уверенность**: {sum(s.get('avg_logprob', 0) for s in result.get('segments', [])) / len(result.get('segments', [])) if result.get('segments') else 'Неизвестно'}

### Сырые данные (JSON)
<details>
<summary>Развернуть полную информацию</summary>

```json
{json.dumps(result, ensure_ascii=False, indent=2)}
```
</details>

---
*Файл создан автоматически с помощью Whisper AI*
"""
    
    # Записываем файл
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return md_file


def transcribe_audio_file(audio_file, model, model_name):
    """Транскрибировать один аудиофайл и создать два типа markdown файлов"""
    print(f"📁 Обрабатываю файл: {audio_file}")
    
    # Получаем информацию о файле
    file_size = os.path.getsize(audio_file)
    file_size_mb = file_size / (1024 * 1024)
    
    # Оцениваем время обработки
    estimated_time = estimate_processing_time(file_size_mb, model_name)
    print(f"🕰️ Оценочное время обработки: {format_duration(estimated_time)}")
    print(f"📄 Размер файла: {file_size_mb:.1f} МБ | Модель: {model_name}")
    
    # Проверяем, не созданы ли уже файлы для этого аудио
    base_name = Path(audio_file).stem
    simple_md_file = f"{base_name}.md"
    detailed_md_file = f"{base_name}_accurate.md"
    
    # Проверяем существование базовых файлов (без timestamp)
    if os.path.exists(simple_md_file) and os.path.exists(detailed_md_file):
        print(f"⚠️  Файлы {simple_md_file} и {detailed_md_file} уже существуют. Пропускаю...")
        send_macos_notification("Уведомление Whisper", f"Файл {audio_file} уже обработан", "Пропускаем")
        return [simple_md_file, detailed_md_file], ""
    
    try:
        print("🎯 Начинаю распознавание...")
        
        # Отправляем уведомление о начале
        send_macos_notification("Начало обработки", f"Обрабатываю: {audio_file}", f"Оценка: {format_duration(estimated_time)}")
        
        start_time = time.time()
        
        # Создаем прогресс-бар
        with tqdm(total=100, desc="🎧 Распознавание", unit="%", ncols=80, 
                  bar_format="{desc}: {percentage:3.0f}%|{bar}| {elapsed} < {remaining}") as pbar:
            
            # Транскрипция с подробными параметрами
            result = whisper.transcribe(
                model, 
                audio_file, 
                verbose=False,          # Отключаем verbose для чистоты прогресс-бара
                word_timestamps=True,   # Временные метки для слов
                temperature=0.2         # Более детерминированный результат
            )
            pbar.update(100)  # Завершаем прогресс-бар
        
        processing_time = time.time() - start_time
        print(f"✅ Распознавание завершено за {format_duration(processing_time)}!")
        
        # Создаем оба markdown файла
        created_files = []
        preview_text = ""
        
        if not os.path.exists(simple_md_file):
            simple_file, preview = create_simple_markdown(audio_file, result)
            created_files.append(simple_file)
            preview_text = preview
            print(f"📝 Создан простой файл: {simple_file}")
        
        if not os.path.exists(detailed_md_file):
            detailed_file = create_detailed_markdown(audio_file, result, model_name)
            created_files.append(detailed_file)
            print(f"📝 Создан подробный файл: {detailed_file}")
        
        # Отправляем уведомление о завершении
        send_macos_notification("✅ Завершено!", f"Транскрипция готова: {audio_file}", preview_text)
        
        return created_files, preview_text
        
    except Exception as e:
        error_msg = f"Ошибка при обработке {audio_file}: {str(e)}"
        print(f"❌ {error_msg}")
        send_macos_notification("❌ Ошибка", error_msg, "Проверьте файл")
        return [], ""


def main():
    """Основная функция"""
    # Обрабатываем аргументы командной строки
    parser = argparse.ArgumentParser(
        description="Автоматическое распознавание аудиофайлов с помощью Whisper"
    )
    parser.add_argument(
        '--model', 
        default='medium',
        help='Модель Whisper для использования (по умолчанию: medium)'
    )
    parser.add_argument(
        '--list-models',
        action='store_true',
        help='Показать все доступные модели'
    )
    
    args = parser.parse_args()
    
    # Показать доступные модели
    if args.list_models:
        print("Доступные модели Whisper:")
        models = ['tiny', 'tiny.en', 'base', 'base.en', 'small', 'small.en', 
                 'medium', 'medium.en', 'large-v1', 'large-v2', 'large-v3', 
                 'large', 'turbo', 'large-v3-turbo']
        for model in models:
            print(f"  - {model}")
        return
    
    print("🎵 Поиск аудиофайлов в текущей директории...")
    
    # Получаем список аудиофайлов
    audio_files = get_audio_files()
    
    if not audio_files:
        print("❌ Аудиофайлы не найдены!")
        return
    
    print(f"✅ Найдено {len(audio_files)} аудиофайлов: {', '.join(audio_files)}")
    
    # Загружаем указанную модель
    print(f"🚀 Загружаю модель Whisper {args.model}...")
    model = whisper.load_model(args.model)
    print("✅ Модель загружена!")
    
    # Обрабатываем каждый файл
    all_created_files = []
    all_words_count = 0
    all_languages = set()
    start_session_time = time.time()
    
    print(f"\n🚀 Начинаю обработку {len(audio_files)} файлов...\n")
    
    for i, audio_file in enumerate(audio_files, 1):
        print(f"\n=== Файл {i}/{len(audio_files)} ===")
        created_files, preview = transcribe_audio_file(audio_file, model, args.model)
        all_created_files.extend(created_files)
        
        # Подсчитываем статистику (примерно)
        if preview:
            words_count = len(preview.split())
            all_words_count += words_count * 10  # Примерное увеличение
        
        print(f"✅ Файл {audio_file} обработан!")
    
    # Подсчитываем общее время сессии
    session_time = time.time() - start_session_time
    
    # Выводим результаты
    print(f"\n🎉 Обработка завершена!")
    print(f"📊 Обработано аудиофайлов: {len(audio_files)}")
    print(f"📄 Создано файлов: {len(all_created_files)}")
    print(f"⏱️ Общее время сессии: {format_duration(session_time)}")
    if all_words_count > 0:
        print(f"💬 Примерное количество слов: {all_words_count:,}")
    
    if all_created_files:
        print("\n📄 Созданные файлы:")
        for file in all_created_files:
            file_type = "📄 Простой" if not file.endswith("_accurate.md") else "🔍 Подробный"
            print(f"  {file_type}: {file}")
    
    # Отправляем итоговое уведомление
    if len(audio_files) > 1:
        summary = f"Обработано {len(audio_files)} файлов за {format_duration(session_time)}"
        send_macos_notification("🎆 Батч завершен!", summary, f"Создано {len(all_created_files)} файлов")


if __name__ == "__main__":
    main()