from pyrogram import Client
import os.path

def GetClient(id: int | str | None = None, hash: str | None = None, session_string: str =None):
	client = Client(name='client', api_id=id, api_hash=hash, in_memory=True, session_string=session_string)
	with client:
		for _ in client.get_dialogs(): pass
		ses_str = client.export_session_string()
	return ses_str, client

def SendFile(app, chat_id, pathfile):
	with app:
		for _ in app.get_dialogs(): pass
		msg = app.send_document(chat_id, rf"{pathfile}")
		return msg.id

def LoadFile(app, chat_id, message_id, outdir='.'):
	with app:
		for _ in app.get_dialogs(): pass
		msg = app.get_messages(chat_id, message_id)
		file = app.download_media(msg, in_memory=True)
		with open(os.path.join(outdir, msg.document.file_name), 'wb') as f:
			f.write(bytes(file.getbuffer()))


def CheckChatID(app, chat_id):
	with app:
		for x in app.get_dialogs():
			if str(x.chat.id) == str(chat_id): return True
		return False