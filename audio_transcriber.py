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


def create_simple_markdown(audio_file, result):
    """Создать простой markdown файл с дословной расшифровкой"""
    base_name = Path(audio_file).stem
    md_file = f"{base_name}.md"
    
    # Создаем простое содержимое markdown файла
    content = f"""# Транскрипция: {audio_file}

{result['text'].strip()}
"""
    
    # Записываем файл
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return md_file


def create_detailed_markdown(audio_file, result, model_name):
    """Создать подробный markdown файл с детальной информацией"""
    base_name = Path(audio_file).stem
    md_file = f"{base_name}_accurate.md"
    
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
    
    # Проверяем, не созданы ли уже файлы для этого аудио
    base_name = Path(audio_file).stem
    simple_md_file = f"{base_name}.md"
    detailed_md_file = f"{base_name}_accurate.md"
    
    if os.path.exists(simple_md_file) and os.path.exists(detailed_md_file):
        print(f"⚠️  Файлы {simple_md_file} и {detailed_md_file} уже существуют. Пропускаю...")
        return [simple_md_file, detailed_md_file]
    
    try:
        print("🎯 Начинаю распознавание...")
        
        # Транскрипция с подробными параметрами
        result = whisper.transcribe(
            model, 
            audio_file, 
            verbose=True,           # Подробный вывод
            word_timestamps=True,   # Временные метки для слов
            temperature=0.2         # Более детерминированный результат
        )
        
        print("✅ Распознавание завершено!")
        
        # Создаем оба markdown файла
        created_files = []
        
        if not os.path.exists(simple_md_file):
            simple_file = create_simple_markdown(audio_file, result)
            created_files.append(simple_file)
            print(f"📝 Создан простой файл: {simple_file}")
        
        if not os.path.exists(detailed_md_file):
            detailed_file = create_detailed_markdown(audio_file, result, model_name)
            created_files.append(detailed_file)
            print(f"📝 Создан подробный файл: {detailed_file}")
        
        return created_files
        
    except Exception as e:
        print(f"❌ Ошибка при обработке {audio_file}: {str(e)}")
        return []


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
    
    for audio_file in audio_files:
        created_files = transcribe_audio_file(audio_file, model, args.model)
        all_created_files.extend(created_files)
    
    # Выводим результаты
    print(f"\n🎉 Обработка завершена!")
    print(f"📊 Обработано аудиофайлов: {len(audio_files)}")
    print(f"📄 Создано файлов: {len(all_created_files)}")
    
    if all_created_files:
        print("📄 Созданные файлы:")
        for file in all_created_files:
            file_type = "📄 Простой" if not file.endswith("_accurate.md") else "🔍 Подробный"
            print(f"  {file_type}: {file}")


if __name__ == "__main__":
    main()