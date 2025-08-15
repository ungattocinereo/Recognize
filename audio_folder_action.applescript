on adding folder items to this_folder after receiving added_items
	-- Получаем путь к папке Recognize на рабочем столе
	set recognizePath to (path to desktop folder as string) & "Recognize:"
	
	-- Проверяем каждый добавленный файл
	repeat with itemRef in added_items
		set itemPath to itemRef as string
		set itemName to name of (info for itemRef)
		
		-- Проверяем, является ли файл аудиофайлом
		if isAudioFile(itemName) then
			-- Показываем уведомление о начале обработки
			display notification "Начинаю распознавание: " & itemName with title "Whisper Transcriber"
			
			-- Получаем POSIX путь для терминала
			set itemPOSIXPath to POSIX path of itemRef
			set folderPOSIXPath to POSIX path of this_folder
			
			-- Формируем команду для терминала
			set terminalCommand to "cd '" & folderPOSIXPath & "' && source /Users/greg/Documents/whisper_env/bin/activate && python /Users/greg/Documents/whisper_env/audio_transcriber.py"
			
			-- Запускаем терминал с командой
			tell application "Terminal"
				activate
				do script terminalCommand
			end tell
			
			-- Ждем немного, чтобы пользователь увидел процесс
			delay 2
		end if
	end repeat
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