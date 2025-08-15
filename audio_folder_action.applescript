on adding folder items to this_folder after receiving added_items
	-- Получаем путь к папке Recognize на рабочем столе
	set recognizePath to (path to desktop folder as string) & "Recognize:"
	
	-- Собираем все аудиофайлы из добавленных элементов
	set audioFiles to {}
	repeat with itemRef in added_items
		set itemPath to itemRef as string
		set itemName to name of (info for itemRef)
		
		-- Проверяем, является ли файл аудиофайлом
		if isAudioFile(itemName) then
			set end of audioFiles to itemName
		end if
	end repeat
	
	-- Если есть аудиофайлы для обработки
	if length of audioFiles > 0 then
		-- Формируем сообщение о количестве файлов
		if length of audioFiles = 1 then
			set fileCountMessage to "1 аудиофайл"
		else
			set fileCountMessage to (length of audioFiles) & " аудиофайлов"
		end if
		
		-- Показываем уведомление о начале обработки
		display notification "Добавлено " & fileCountMessage & " в очередь обработки" with title "🎵 Whisper Transcriber" subtitle "Запускаю обработку..."
		
		-- Получаем POSIX путь для терминала
		set folderPOSIXPath to POSIX path of this_folder
		
		-- Проверяем, есть ли уже активное окно Terminal с нашим процессом
		set shouldCreateNewWindow to true
		tell application "Terminal"
			if (count of windows) > 0 then
				repeat with terminalWindow in windows
					set windowProcesses to (do shell script "ps aux | grep '[p]ython.*audio_transcriber' | wc -l")
					if windowProcesses as integer > 0 then
						-- Есть активный процесс транскрипции
						set shouldCreateNewWindow to false
						exit repeat
					end if
				end repeat
			end if
			
			if shouldCreateNewWindow then
				-- Формируем команду для терминала
				set terminalCommand to "echo '🎵 Запуск Whisper Transcriber...' && cd '" & folderPOSIXPath & "' && source /Users/greg/Documents/whisper_env/bin/activate && python /Users/greg/Documents/whisper_env/audio_transcriber.py"
				
				activate
				do script terminalCommand
			else
				-- Показываем уведомление, что файлы будут обработаны в существующей очереди
				display notification "Файлы будут обработаны после завершения текущей обработки" with title "⏳ Очередь обработки" subtitle "Terminal уже активен"
			end if
		end tell
	end if
end adding folder items to

-- Функция для проверки, является ли файл аудиофайлом
on isAudioFile(fileName)
	set audioExtensions to {".mp3", ".wav", ".m4a", ".flac", ".ogg", ".wma", ".aac"}
	set fileName to fileName as string
	
	repeat with ext in audioExtensions
		if fileName ends with ext then
			return true
		end if
	end repeat
	
	return false
end isAudioFile