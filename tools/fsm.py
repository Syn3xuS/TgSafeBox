import sqlite3, pickle, os
from pathlib import Path

CONFIGPATH = os.path.join(str(Path('~').expanduser()), '.tgsafebox.conf')

def get_paths(paths: list)-> list[list] :
	RealPathFiles = []
	HowToSaveDirs = []
	HowToSaveFiles = []
	for path in paths:
		if not os.path.exists(path):
			raise Exception(f"НЕСУЩЕСТВУЮЩИЙ ПУТЬ: {path}")
	for path in paths:
		if os.path.isdir(path):
			lastdir = os.getcwd()
			os.chdir(path)
			path = os.getcwd()
			title = os.path.split(os.path.dirname(f"{os.path.realpath(path)}/."))[-1]
			HowToSaveDirs.append(title)
			for dirpath, dirnames, filenames in os.walk(path):
				for dirname in dirnames:
					HowToSaveDirs.append(os.path.join(title, os.path.relpath(os.path.join(dirpath, dirname))))
				for filename in filenames:
					RealPathFiles.append(os.path.realpath(os.path.join(dirpath, filename)))
					HowToSaveFiles.append(os.path.join(title, os.path.relpath(os.path.join(dirpath, filename))))
			os.chdir(lastdir)
		elif os.path.isfile(path):
			RealPathFiles.append(os.path.realpath(path))
			HowToSaveFiles.append(os.path.basename(path))
	return [HowToSaveDirs, RealPathFiles, HowToSaveFiles]


def CreateConfig():
	with sqlite3.connect(CONFIGPATH) as conn:
		cursor = conn.cursor()
		cursor.execute("CREATE TABLE IF NOT EXISTS clients (api_id INTEGER, api_hash TEXT, session_string TEXT)")

def ClientList():
	with sqlite3.connect(CONFIGPATH) as conn:
		cursor = conn.cursor()
		cursor.execute("SELECT * FROM clients")
		clients = cursor.fetchall()
	return clients

def ClientAdd(api_id, api_hash, session_string):
	with sqlite3.connect(CONFIGPATH) as conn:
		cursor = conn.cursor()
		cursor.execute("INSERT INTO clients VALUES (?, ?, ?)", (api_id, api_hash, session_string))

def ClientDel(number):
	with sqlite3.connect(CONFIGPATH) as conn:
		cursor = conn.cursor()
		cursor.execute("DELETE FROM clients WHERE rowid = ?", (number, ))


def BoxPartWrite(partname:str, line:str, data):
	with sqlite3.connect(partname) as conn:
		cursor = conn.cursor()
		cursor.execute("CREATE TABLE IF NOT EXISTS data (key TEXT PRIMARY KEY, value BLOB)")
		cursor.execute("INSERT INTO data VALUES (?, ?)", (line, pickle.dumps(data)))

def BoxPartRead(partname:str, line:str):
	with sqlite3.connect(partname) as conn:
		cursor = conn.cursor()
		cursor.execute("SELECT value FROM data WHERE key = ?", (line,))
		row = cursor.fetchone()
		cursor.close()
	conn.close()
	return pickle.loads(row[0]) if row else None

def CreateBox(boxname):
	with sqlite3.connect(boxname) as conn:
		cursor = conn.cursor()
		cursor.execute("CREATE TABLE IF NOT EXISTS info (parameter TEXT PRIMARY KEY, value TEXT)")
		cursor.executemany("""INSERT OR IGNORE INTO info VALUES(?, ?)""", [
			('Name', ''),
			('About', ''),
			('Date', ''),
			('Key', ''),
			('Size', ''),
			('Parts', ''),
			('Dirs', ''),
			('Files', ''),
			('Cloud_id', '')
			])
		cursor.execute("CREATE TABLE IF NOT EXISTS dirs (path TEXT PRIMARY KEY)")
		cursor.execute("CREATE TABLE IF NOT EXISTS files (path TEXT PRIMARY KEY, size TEXT, value BLOB)")
		cursor.execute("CREATE TABLE IF NOT EXISTS parts (part TEXT PRIMARY KEY, msg_id)")

def SetBox(boxname, argument, value):
	with sqlite3.connect(boxname) as conn:
		cursor = conn.cursor()
		cursor.execute("""REPLACE INTO info VALUES (?, ?)""", (argument, value))

def GetParameterFromBox(boxname, argument):
	with sqlite3.connect(boxname) as conn:
		cursor = conn.cursor()
		cursor.execute("""SELECT value FROM info WHERE parameter = ?""", (argument, ))
		res = cursor.fetchone()
		return res[0] if res else None

def SetDirInBox(boxname, pathname):
	with sqlite3.connect(boxname) as conn:
		cursor = conn.cursor()
		cursor.execute("INSERT OR REPLACE INTO dirs VALUES (? )", (pickle.dumps(pathname.split(os.sep)),))

def SetFileInBox(boxname, pathname, size, data):
	with sqlite3.connect(boxname) as conn:
		cursor = conn.cursor()
		cursor.execute("INSERT OR REPLACE INTO files VALUES (?, ?, ?)", (pickle.dumps(pathname.split(os.sep)), size, pickle.dumps(data)))

def SetPartInBox(boxname, part, msg_id):
	with sqlite3.connect(boxname) as conn:
		cursor = conn.cursor()
		cursor.execute("INSERT OR REPLACE INTO parts VALUES (?, ?)", (part, msg_id))

def GetDirsFromBox(boxname):
	with sqlite3.connect(boxname) as conn:
		cursor = conn.cursor()
		cursor.execute("""SELECT * FROM dirs""")
		res = cursor.fetchall()
		return [os.path.join(*pickle.loads(x[0])) for x in res] if res else None

def GetFilesFromBox(boxname):
	with sqlite3.connect(boxname) as conn:
		cursor = conn.cursor()
		cursor.execute("""SELECT * FROM files""")
		res = cursor.fetchall()
		return [[os.path.join(*pickle.loads(x[0])),x[1], pickle.loads(x[2]) ] for x in res] if res else None

def GetPartInBox(boxname, part):
	with sqlite3.connect(boxname) as conn:
		cursor = conn.cursor()
		cursor.execute("SELECT msg_id FROM parts WHERE part = ?", (part, ))
		res = cursor.fetchone()
		return res[0] if res else None
