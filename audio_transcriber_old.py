#!/usr/bin/env python3
"""
Автоматическое распознавание аудиофайлов с помощью Whisper
Скрипт ищет аудиофайлы в текущей директории и создает подробные .md файлы с результатами
"""

import os
import glob
import whisper
import datetime
from pathlib import Path
import json


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


def create_markdown_report(audio_file, result):
    """Создать подробный markdown файл с результатами транскрипции"""
    base_name = Path(audio_file).stem
    md_file = f"{base_name}.md"
    
    # Получаем информацию о файле
    file_size = os.path.getsize(audio_file)
    file_size_mb = file_size / (1024 * 1024)
    
    # Текущее время
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Создаем содержимое markdown файла
    content = f"""# Транскрипция аудиофайла: {audio_file}

## Информация о файле
- **Имя файла**: `{audio_file}`
- **Размер**: {file_size_mb:.2f} МБ
- **Дата обработки**: {timestamp}
- **Модель Whisper**: large-v3-turbo (самая большая и быстрая)

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


def transcribe_audio_file(audio_file, model):
    """Транскрибировать один аудиофайл"""
    print(f"📁 Обрабатываю файл: {audio_file}")
    
    # Проверяем, не создан ли уже .md файл для этого аудио
    base_name = Path(audio_file).stem
    md_file = f"{base_name}.md"
    
    if os.path.exists(md_file):
        print(f"⚠️  Файл {md_file} уже существует. Пропускаю...")
        return md_file
    
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
        
        # Создаем markdown файл
        md_file = create_markdown_report(audio_file, result)
        print(f"📝 Создан файл: {md_file}")
        
        return md_file
        
    except Exception as e:
        print(f"❌ Ошибка при обработке {audio_file}: {str(e)}")
        return None


def main():
    """Основная функция"""
    print("🎵 Поиск аудиофайлов в текущей директории...")
    
    # Получаем список аудиофайлов
    audio_files = get_audio_files()
    
    if not audio_files:
        print("❌ Аудиофайлы не найдены!")
        return
    
    print(f"✅ Найдено {len(audio_files)} аудиофайлов: {', '.join(audio_files)}")
    
    # Загружаем самую большую и быструю модель
    print("🚀 Загружаю модель Whisper large-v3-turbo...")
    model = whisper.load_model("large-v3-turbo")
    print("✅ Модель загружена!")
    
    # Обрабатываем каждый файл
    processed_files = []
    
    for audio_file in audio_files:
        md_file = transcribe_audio_file(audio_file, model)
        if md_file:
            processed_files.append(md_file)
    
    # Выводим результаты
    print(f"\n🎉 Обработка завершена!")
    print(f"📊 Обработано файлов: {len(processed_files)}")
    
    if processed_files:
        print("📄 Созданные файлы:")
        for file in processed_files:
            print(f"  • {file}")


if __name__ == "__main__":
    main()