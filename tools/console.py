from tools import fsm
import datetime

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
