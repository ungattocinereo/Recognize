-- Property переменные для отслеживания состояния
property isWaitingForStabilization : false
property lastFileCount : 0
property maxWaitTime : 10 -- максимальное время ожидания в секундах

on adding folder items to this_folder after receiving added_items
	-- Если уже ждем стабилизации, просто выходим (избегаем множественных срабатываний)
	if isWaitingForStabilization then
		return
	end if
	
	-- Проверяем, есть ли аудиофайлы среди добавленных
	set hasAudioFiles to false
	repeat with itemRef in added_items
		set itemName to name of (info for itemRef)
		if isAudioFile(itemName) then
			set hasAudioFiles to true
			exit repeat
		end if
	end repeat
	
	-- Если нет аудиофайлов, ничего не делаем
	if not hasAudioFiles then
		return
	end if
	
	-- Устанавливаем флаг ожидания
	set isWaitingForStabilization to true
	
	-- Показываем уведомление о начале ожидания
	display notification "Обнаружены новые аудиофайлы. Ожидаю стабилизации..." with title "🎵 Whisper Transcriber" subtitle "Анализирую очередь..."
	
	try
		-- Ждем стабилизации файлов
		set stableFileCount to waitForFileStabilization(this_folder)
		
		if stableFileCount > 0 then
			-- Запускаем обработку всех стабилизированных файлов
			launchTranscriptionProcess(this_folder, stableFileCount)
		else
			display notification "Аудиофайлы не найдены после стабилизации" with title "⚠️ Whisper Transcriber" subtitle "Проверьте папку"
		end if
		
	on error errMsg
		display notification "Ошибка при ожидании стабилизации: " & errMsg with title "❌ Whisper Transcriber" subtitle "Попробуйте еще раз"
	end try
	
	-- Сбрасываем флаг ожидания
	set isWaitingForStabilization to false
	set lastFileCount to 0
end adding folder items to

-- Функция для подсчета аудиофайлов в папке
on countAudioFilesInFolder(folderRef)
	set audioCount to 0
	try
		tell application "Finder"
			set folderItems to every item of folderRef
			repeat with fileItem in folderItems
				set fileName to name of fileItem
				if isAudioFile(fileName) then
					set audioCount to audioCount + 1
				end if
			end repeat
		end tell
	on error
		-- Если ошибка доступа к папке, возвращаем 0
		set audioCount to 0
	end try
	return audioCount
end countAudioFilesInFolder

-- Функция ожидания стабилизации файлов
on waitForFileStabilization(folderRef)
	set waitCycles to 0
	set maxCycles to 5 -- максимум 5 циклов по 2 секунды = 10 секунд
	
	-- Получаем начальное количество файлов
	set lastFileCount to countAudioFilesInFolder(folderRef)
	
	repeat while waitCycles < maxCycles
		-- Ждем 2 секунды
		delay 2
		set waitCycles to waitCycles + 1
		
		-- Проверяем текущее количество файлов
		set currentFileCount to countAudioFilesInFolder(folderRef)
		
		-- Если количество не изменилось - файлы стабилизировались
		if currentFileCount = lastFileCount then
			return currentFileCount
		end if
		
		-- Обновляем последний счетчик
		set lastFileCount to currentFileCount
		
		-- Показываем прогресс ожидания
		if waitCycles < maxCycles then
			display notification "Ожидание стабилизации... (" & waitCycles & "/" & maxCycles & ")" with title "⏳ Whisper Transcriber" subtitle "Файлов: " & currentFileCount
		end if
	end repeat
	
	-- Если дошли до максимума циклов, возвращаем последний счетчик
	return lastFileCount
end waitForFileStabilization

-- Функция запуска процесса транскрипции
on launchTranscriptionProcess(folderRef, fileCount)
	try
		-- Формируем сообщение о количестве файлов
		if fileCount = 1 then
			set fileCountMessage to "1 аудиофайл"
		else
			set fileCountMessage to fileCount & " аудиофайлов"
		end if
		
		-- Проверяем, есть ли уже активный процесс
		set windowProcesses to (do shell script "ps aux | grep '[p]ython.*audio_transcriber' | wc -l")
		if windowProcesses as integer > 0 then
			display notification "Файлы будут обработаны после завершения текущей обработки" with title "⏳ Очередь обработки" subtitle fileCountMessage & " в ожидании"
			return
		end if
		
		-- Показываем уведомление о начале обработки
		display notification "Запускаю обработку " & fileCountMessage with title "🚀 Whisper Transcriber" subtitle "Открываю Terminal..."
		
		-- Получаем POSIX путь для терминала
		set folderPOSIXPath to POSIX path of folderRef
		
		-- Формируем команду для терминала
		set terminalCommand to "echo '🎵 Запуск Whisper Transcriber для " & fileCount & " файлов...' && cd '" & folderPOSIXPath & "' && source /Users/greg/Documents/whisper_env/bin/activate && python /Users/greg/Documents/whisper_env/audio_transcriber.py"
		
		-- Запускаем терминал с командой
		tell application "Terminal"
			activate
			do script terminalCommand
		end tell
		
	on error errMsg
		display notification "Ошибка запуска: " & errMsg with title "❌ Whisper Transcriber" subtitle "Попробуйте вручную"
	end try
end launchTranscriptionProcess

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