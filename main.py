import logging, argparse, datetime
from tools import crypto, fsm, tg, console

#Настраиваем логирование
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler('log.txt', encoding='UTF-8')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
print_handler = logging.StreamHandler()
print_handler.setFormatter(logging.Formatter('%(message)s'))
logger.addHandler(file_handler)
logger.addHandler(print_handler)


def _client(args):
	fsm.CreateConfig()
	match args.client_command:
		case 'list':
			clients = fsm.ClientList()
			print("СПИСОК КЛИЕНТОВ:")
			if (not clients):
				print('\tСпискок клиентов пуст!')
				return
			for number, client in enumerate(clients):
				print("\t #{} - api_id{} - api_hash{}".format(number+1, client[0], client[1]))
		case 'add':
			clients = fsm.ClientList()
			if(clients):
				for client in clients:
					if(args.id==client[0] and args.hash==client[1]):
						print("Такой клиент уже есть в конфиге")
						print("> #{} - api_id{} - api_hash{}".format(number+1, client[0], client[1]))
						return
			session, client = tg.GetClient(args.id, args.hash)
			fsm.ClientAdd(args.id, args.hash, session)
		case 'del':
			clients = fsm.ClientList()
			if(not clients):
				print('\tСпискок клиентов пуст!')
				return
			for number, client in enumerate(clients):
				if(args.number==number+1):
					fsm.ClientDel(args.number)
					print("Клиент успешно удалён")
					print("> #{} - api_id={} - api_hash={}".format(number+1, client[0], client[1]))
					return
			print("Клиент не найден")


def _upload(args):
	clients = fsm.ClientList()
	session = None
	for number, client in enumerate(clients):
		if(args.client_number==number+1):
			session = client[2]
			break
	if(not session):
		print("Аккаунт не найден")
		return
	ses_str, app = tg.GetClient(session_string=session)
	chatid = args.cloud_id
	
	if not tg.CheckChatID(app, chatid):
		print("Аккаунт не имеет доступа к чату либо чата не существует")
		raise Exception("Аккаунт не имеет доступа к чату либо чата не существует")
	
	name = args.box_name
	configname = f"{name}.tsb"
	key = crypto.GenKey()
	date = datetime.datetime.now()
	size = 0
	dirnames, filepaths, filenames = fsm.get_paths(args.paths)
	parts = 0
	statuspart = 0
	logs = []
	errors = []

	fsm.CreateBox(configname)
	fsm.SetBox(configname, 'Name', name)
	fsm.SetBox(configname, 'Date', str(date))
	fsm.SetBox(configname, 'Key', key)
	fsm.SetBox(configname, 'Dirs', len(dirnames))
	fsm.SetBox(configname, 'Files', len(filepaths))
	fsm.SetBox(configname, 'Cloud_id', chatid)
	if args.about_filepath:
		if not fsm.os.path.isdir(args.about_filepath):
			raise Exception(f"Файл {args.about_filepath} не существует.")

		with open(args.about_filepath, 'r', encoding='utf-8') as file:
			about_text = file.read()
		fsm.SetBox(configname, 'About', about_text)

	for dr in dirnames:
		fsm.SetDirInBox(configname, dr)

	for i, file in enumerate(filepaths):
		filedict = {}
		status = f"Запись файла {i + 1}/{len(filepaths)}: {file}"
		logs.append(f"[INFO] {status}")
		console.update_console(status, file, parts, statuspart, int((i + 1) / len(filepaths) * 100), logs, errors)
		with open(file, 'rb') as fin:
			while True:
				resin = fin.read(1 * 1024 * 1024)
				if not resin:
					if i == len(filenames) - 1:
						status = f'Отправка части: {name}-{parts}'
						logs.append(f"[INFO] {status}")
						console.update_console(status, file, parts, statuspart, int((i + 1) / len(filepaths) * 100), logs, errors)
						msgid = tg.SendFile(app, chatid, f'{name}-{parts}')
						fsm.SetPartInBox(configname, f'{name}-{parts}', msgid)
						fsm.os.remove(f'{name}-{parts}')
					
					filesize = fsm.os.path.getsize(file)
					size += filesize
					fsm.SetFileInBox(configname, filenames[i], str(filesize), filedict)
					break

				fsm.BoxPartWrite(f'{name}-{parts}', str(statuspart), crypto.Encrypt(resin, key))
				if str(parts) not in filedict:
					filedict[str(parts)] = []
				filedict[str(parts)].append(statuspart)
				statuspart += 1

				if fsm.os.path.getsize(f'{name}-{parts}') > 32 * 1024 * 1024:
					status = f'Отправка части: {name}-{parts}'
					logs.append(f"[INFO] {status}")
					console.update_console(status, file, parts, statuspart, int((i + 1) / len(filepaths) * 100), logs, errors)
					msgid = tg.SendFile(app, chatid, f'{name}-{parts}')
					fsm.SetPartInBox(configname, f'{name}-{parts}', msgid)
					fsm.os.remove(f'{name}-{parts}')
					parts += 1

	fsm.SetBox(configname, 'Size', size)
	fsm.SetBox(configname, 'Parts', parts)
	status = "Успешно загружено!"
	logs.append(f"[INFO] {status}")
	console.update_console(status, "", 0, 0, 100, logs, errors)

def _download(args):
	clients = fsm.ClientList()
	session = None
	for number, client in enumerate(clients):
		if(args.client_number==number+1):
			session = client[2]
			break
	if(not session):
		print("Аккаунт не найден")
		return
	ses_str, app = tg.GetClient(session_string=session)
	configname = fsm.os.path.realpath(args.box_name)
	if (not fsm.os.path.isfile(configname)):
		print("Такой коробки нет!")
		return
	name = fsm.GetParameterFromBox(configname, 'Name')
	outdir = fsm.os.path.join(fsm.os.path.realpath(args.out_dir), name)
	fsm.os.makedirs(outdir, exist_ok=True)
	chatid = fsm.GetParameterFromBox(configname, 'Cloud_id')
	key = fsm.GetParameterFromBox(configname, 'Key')
	logs = []
	errors = []

	if not tg.CheckChatID(app, chatid):
		error = "Аккаунт не имеет доступа к чату либо чата не существует"
		print(error)
		errors.append(f"[ERROR] {error}")
		raise Exception(error)

	for dr in fsm.GetDirsFromBox(configname):
		fsm.os.makedirs(fsm.os.path.join(outdir, dr), exist_ok=True)

	total_size = int(fsm.GetParameterFromBox(configname, 'Size'))  # общий размер файлов
	downloaded_size = 0

	current_chunk = None
	current_chunk_file = None

	for file_info in fsm.GetFilesFromBox(configname):
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
				console.update_console(status, filename, chunk_number, 0, progress, logs, errors)
				current_chunk_file = chunk_number
				tg.LoadFile(app, chatid, fsm.GetPartInBox(configname, f'{name}-{chunk_number}'))
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
			console.update_console(status, filename, chunk_number, line, progress, logs, errors)
		fout.close()

	if current_chunk_file:
		fsm.os.remove(f"{name}-{current_chunk_file}")
	status = "Успешно загружено!"
	logs.append(f"[INFO] {status}")
	console.update_console(status, "", 0, 0, 100, logs, errors)


def _info(args):
	configname = args.box_name
	if (not fsm.os.path.isfile(configname)): raise Exception("Такого файда нет!")
	name = fsm.GetParameterFromBox(configname, 'Name')
	about = fsm.GetParameterFromBox(configname, 'About')
	date = fsm.GetParameterFromBox(configname, 'Date')
	key = fsm.GetParameterFromBox(configname, 'Key')
	size = fsm.GetParameterFromBox(configname, 'Size')
	parts = fsm.GetParameterFromBox(configname, 'Parts')
	dirs_count = fsm.GetParameterFromBox(configname, 'Dirs')
	files_count = fsm.GetParameterFromBox(configname, 'Files')
	cloud_id = fsm.GetParameterFromBox(configname, 'Cloud_id')
	
	dirs = fsm.GetDirsFromBox(configname)
	files = fsm.GetFilesFromBox(configname)
	
	logger.info(f"Информация о коробке '{configname}':")
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
		if((i)%10==0):
			input('Нажмите Enter чтобы продолжить')
			print('\033[A\033[K', end='')
		
		print(f"  - {d}")
	
	print("\nФайлы:")
	for i, f in enumerate(files):
		filename, filesize, fileparts = f
		if((i)%10==0):
			input('Нажмите Enter чтобы продолжить')
			print('\033[A\033[K', end='')
		print(f"  - {filename} (размер: {filesize} байт, части: {fileparts})")


def main():
	main_parser = argparse.ArgumentParser()

	subparsers = main_parser.add_subparsers(dest='command', required=True)

	upload_parser = subparsers.add_parser('upload')
	upload_parser.add_argument('client_number', type=int)
	upload_parser.add_argument('cloud_id', type=int)
	upload_parser.add_argument('box_name')
	upload_parser.add_argument('paths', nargs='+')
	upload_parser.add_argument('-af', '--about_filepath', default=None, required=False)
	upload_parser.set_defaults(func=_upload)
	
	download_parser = subparsers.add_parser('download')
	download_parser.add_argument('client_number', type=int)
	download_parser.add_argument('box_name')
	download_parser.add_argument('-o', '--out_dir', default='.', required=False)
	download_parser.set_defaults(func=_download)

	client_parsers = subparsers.add_parser('client')
	client_command_parser = client_parsers.add_subparsers(dest='client_command', required=True)
	client_list_parser = client_command_parser.add_parser('list')
	client_add_parser = client_command_parser.add_parser('add')
	client_add_parser.add_argument('id', type=int)
	client_add_parser.add_argument('hash')
	client_del_parser = client_command_parser.add_parser('del')
	client_del_parser.add_argument('number', type=int)
	client_parsers.set_defaults(func=_client)


	info_parser = subparsers.add_parser('info')
	info_parser.add_argument('box_name', type=str)
	info_parser.set_defaults(func=_info)

	args = main_parser.parse_args()
	#print(args)
	args.func(args)


if __name__ == '__main__': main()