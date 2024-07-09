import sys, datetime, logging, platform
import crypto, fsm, tg

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def clear_console():
	fsm.os.system('cls' if fsm.os.name == 'nt' else 'clear')

def update_console(status, current_file, current_part, current_line, progress, logs, errors):
	clear_console()
	print("--------------------------------------------")
	print("      TgSafeBox Utility    by Syn3xuS       ")
	print("--------------------------------------------")
	print(f"Дата и время: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
	print("--------------------------------------------")
	print(f"Статус: {status}")
	print()
	print(f"Действие: {logs[-1] if logs else 'Нет данных'}")
	print(f"Файл: {current_file}")
	print(f"Часть: {current_part}")
	print(f"Строка: {current_line}")
	print("--------------------------------------------")
	print("Логи:")
	for log in logs[-10:]:
		print(log)
	print("--------------------------------------------")
	print("Ошибки и предупреждения:")
	for error in errors:
		print(error)
	print("--------------------------------------------")
	print("Прогресс выполнения:")
	print(f"[{'#' * (progress // 10)}{'-' * (10 - progress // 10)}] {progress}%")
	print("--------------------------------------------")

def _client(args):
	if len(args) != 5:
		logger.error("Неверное количество аргументов. Использование: -client <ClientName> <api_id> <api_hash>")
		raise Exception("Неверное количество аргументов. Использование: -client <ClientName> <api_id> <api_hash>")
	logger.info("Создание и инициализация клиента Telegram")
	tg.GetClient(args[2], int(args[3]), args[4])

def _upload(args):
	print(args)
	if len(args) < 6:
		logger.error("Неверное количество аргументов. Использование: -upload <ClientName> <chat_id> <name> <file_or_directory_paths>")
		raise Exception("Неверное количество аргументов. Использование: -upload <ClientName> <chat_id> <name> <file_or_directory_paths>")
	app = tg.GetClient(ClientName=args[2])
	
	if not tg.CheckChatID(app, args[3]):
		logger.error("Аккаунт не имеет доступа к чату либо чата не существует")
		raise Exception("Аккаунт не имеет доступа к чату либо чата не существует")
	
	chatid = args[3]
	name = args[4]
	configname = f"{args[4]}.tsb"
	key = crypto.GenKey()
	date = datetime.datetime.now()
	size = 0
	dirnames, filepaths, filenames = fsm.get_paths(args[5:])
	parts = 0
	statuspart = 0
	logs = []
	errors = []

	fsm.CreateBoxConfig(configname)
	fsm.SetBoxConfig(configname, 'Name', name)
	fsm.SetBoxConfig(configname, 'Date', str(date))
	fsm.SetBoxConfig(configname, 'Key', key)
	fsm.SetBoxConfig(configname, 'Dirs', len(dirnames))
	fsm.SetBoxConfig(configname, 'Files', len(filepaths))
	fsm.SetBoxConfig(configname, 'Cloud_id', chatid)

	for dr in dirnames:
		fsm.SetDirInBoxConfig(configname, dr)

	for i, file in enumerate(filepaths):
		filedict = {}
		status = f"Запись файла {i + 1}/{len(filepaths)}: {file}"
		logs.append(f"[INFO] {status}")
		update_console(status, file, parts, statuspart, int((i + 1) / len(filepaths) * 100), logs, errors)
		with open(file, 'rb') as fin:
			while True:
				resin = fin.read(1 * 1024 * 1024)
				if not resin:
					if i == len(filenames) - 1:
						status = f'Отправка части: {name}-{parts}'
						logs.append(f"[INFO] {status}")
						update_console(status, file, parts, statuspart, int((i + 1) / len(filepaths) * 100), logs, errors)
						msgid = tg.SendFile(app, chatid, f'{name}-{parts}')
						fsm.SetPartInBoxConfig(configname, f'{name}-{parts}', msgid)
						fsm.os.remove(f'{name}-{parts}')
					
					filesize = fsm.os.path.getsize(file)
					size += filesize
					fsm.SetFileInBoxConfig(configname, filenames[i], str(filesize), filedict)
					break

				fsm.BoxPartWrite(f'{name}-{parts}', str(statuspart), crypto.Encrypt(resin, key))
				if str(parts) not in filedict:
					filedict[str(parts)] = []
				filedict[str(parts)].append(statuspart)
				statuspart += 1

				if fsm.os.path.getsize(f'{name}-{parts}') > 32 * 1024 * 1024:
					status = f'Отправка части: {name}-{parts}'
					logs.append(f"[INFO] {status}")
					update_console(status, file, parts, statuspart, int((i + 1) / len(filepaths) * 100), logs, errors)
					msgid = tg.SendFile(app, chatid, f'{name}-{parts}')
					fsm.SetPartInBoxConfig(configname, f'{name}-{parts}', msgid)
					fsm.os.remove(f'{name}-{parts}')
					parts += 1

	fsm.SetBoxConfig(configname, 'Size', size)
	fsm.SetBoxConfig(configname, 'Parts', parts)
	status = "Успешно загружено!"
	logs.append(f"[INFO] {status}")
	update_console(status, "", 0, 0, 100, logs, errors)

def _download(args):
	if len(args) != 5:
		logger.error("Неверное количество аргументов. Использование: -download <ClientName> <config_name> <output_directory>")
		raise Exception("Неверное количество аргументов. Использование: -download <ClientName> <config_name> <output_directory>")

	app = tg.GetClient(ClientName=args[2])
	configname = args[3]
	name = fsm.GetParameterFromBoxConfig(configname, 'Name')
	outdir = fsm.os.path.join(fsm.os.path.realpath(args[4]), name)
	fsm.os.makedirs(outdir, exist_ok=True)
	chatid = fsm.GetParameterFromBoxConfig(configname, 'Cloud_id')
	key = fsm.GetParameterFromBoxConfig(configname, 'Key')
	logs = []
	errors = []

	if not tg.CheckChatID(app, chatid):
		error = "Аккаунт не имеет доступа к чату либо чата не существует"
		logger.error(error)
		errors.append(f"[ERROR] {error}")
		raise Exception(error)

	for dr in fsm.GetDirsFromBoxConfig(configname):
		fsm.os.makedirs(fsm.os.path.join(outdir, dr), exist_ok=True)

	total_size = int(fsm.GetParameterFromBoxConfig(configname, 'Size'))  # общий размер файлов
	downloaded_size = 0

	current_chunk = None
	current_chunk_file = None

	for file_info in fsm.GetFilesFromBoxConfig(configname):
		filename = fsm.os.path.join(outdir, file_info[0])
		size = int(file_info[1])
		chunks_needed = file_info[2].keys()
		fout = open(filename, 'wb')
		for chunk_number in chunks_needed:
			if current_chunk != chunk_number:
				if current_chunk_file:
					fsm.os.remove(f"{name}-{current_chunk_file}")
				status = f"Скачивание части: {name}-{chunk_number}"
				logs.append(f"[INFO] {status}")
				progress = int(downloaded_size / total_size * 100)
				update_console(status, filename, chunk_number, 0, progress, logs, errors)
				current_chunk_file = chunk_number
				tg.LoadFile(app, chatid, fsm.GetPartInBoxConfig(configname, f'{name}-{chunk_number}'))
				current_chunk = chunk_number
			lines = file_info[2][chunk_number]
			for line in lines:
				res = fsm.BoxPartRead(f"{name}-{current_chunk_file}", line)
				decrypted_data = crypto.Decrypt(res, key)
				fout.write(decrypted_data)
				downloaded_size += len(decrypted_data)  # обновляем количество загруженных данных
			status = f"Обработка строк {lines} в части {chunk_number} для файла {filename}"
			logs.append(f"[INFO] {status}")
			progress = int(downloaded_size / total_size * 100)
			update_console(status, filename, chunk_number, line, progress, logs, errors)
		fout.close()

	if current_chunk_file:
		fsm.os.remove(f"{name}-{current_chunk_file}")
	status = "Успешно загружено!"
	logs.append(f"[INFO] {status}")
	update_console(status, "", 0, 0, 100, logs, errors)


def _info(args):
	if len(args) != 3:
		logger.error("Неверное количество аргументов для получения информации.")
		raise Exception("Неверное количество аргументов для получения информации.")
	
	configname = args[2]
	name = fsm.GetParameterFromBoxConfig(configname, 'Name')
	about = fsm.GetParameterFromBoxConfig(configname, 'About')
	date = fsm.GetParameterFromBoxConfig(configname, 'Date')
	key = fsm.GetParameterFromBoxConfig(configname, 'Key')
	size = fsm.GetParameterFromBoxConfig(configname, 'Size')
	parts = fsm.GetParameterFromBoxConfig(configname, 'Parts')
	dirs_count = fsm.GetParameterFromBoxConfig(configname, 'Dirs')
	files_count = fsm.GetParameterFromBoxConfig(configname, 'Files')
	cloud_id = fsm.GetParameterFromBoxConfig(configname, 'Cloud_id')
	
	dirs = fsm.GetDirsFromBoxConfig(configname)
	files = fsm.GetFilesFromBoxConfig(configname)
	
	print(f"Информация о коробке '{configname}':")
	print(f"  Имя: {name}")
	print( "  Описание: {}".format("\n\t\t"+about if about else about))
	print(f"  Дата создания: {date}")
	print(f"  Ключ шифрования: {key}")
	print(f"  Общий размер: {size} байт")
	print(f"  Количество частей: {int(parts)+1}")
	print(f"  Количество директорий: {dirs_count}")
	print(f"  Количество файлов: {files_count}")
	print(f"  ID облачного чата: {cloud_id}")
	
	print("\nДиректории:")
	for i, d in enumerate(dirs):
		if((i+1)%10==0):
			input('Нажмите Enter чтобы продолжить')
			print('\033[A', end='')
		
		print(f"  - {d}")
	
	print("\nФайлы:")
	for i, f in enumerate(files):
		filename, filesize, fileparts = f
		if((i+1)%10==0):
			input('Нажмите Enter чтобы продолжить')
			print('\033[A', end='')
		print(f"  - {filename} (размер: {filesize} байт, части: {fileparts})")

def _setabout(args):
	if len(args) != 4:
		logger.error("Неверное количество аргументов для установки описания.")
		raise Exception("Неверное количество аргументов для установки описания.")
	
	configname = args[2]
	about_file_path = args[3]
	
	if not fsm.os.path.exists(about_file_path):
		logger.error(f"Файл {about_file_path} не существует.")
		raise Exception(f"Файл {about_file_path} не существует.")
	
	with open(about_file_path, 'r', encoding='utf-8') as file:
		about_text = file.read()
	
	fsm.SetBoxConfig(configname, 'About', about_text)
	logger.info(f"Описание для '{configname}' успешно установлено из файла '{about_file_path}'.")

def _help(args):
	help_text = """
Использование: main.py [-client|-upload|-download|-info|-setabout|-h|-help] [args]

Доступные команды:
	-client <ClientName> <api_id> <api_hash>
		Создание и инициализация клиента Telegram.

	-upload <ClientName> <chat_id> <name> <file_or_directory_paths>
		Загрузка файлов или директорий в Telegram чат.

	-download <ClientName> <config_name> <output_directory>
		Скачивание файлов из Telegram чата с использованием конфигурационного файла.

	-info <config_name>
		Получение всей информации о заданной 'коробке' (tsb файл).

	-setabout <config_name> <about_file_path>
		Установка описания для конфигурационного файла из текстового файла.

	-h, -help
		Показать эту справочную информацию.
	"""
	print(help_text)

def main():
	args = sys.argv
	if len(args) <= 1:
		logger.error("Слишком мало аргументов.")
		raise Exception("Слишком мало аргументов.")
	
	command_map = {
		'-client': _client,
		'-upload': _upload,
		'-download': _download,
		'-info': _info,
		'-setabout': _setabout,
		'-h': _help,
		'-help': _help
	}

	command = args[1]
	if command not in command_map:
		logger.error("Неверный аргумент")
		raise Exception("Неверный аргумент")
	
	command_map[command](args)

if __name__ == '__main__':
	main()
