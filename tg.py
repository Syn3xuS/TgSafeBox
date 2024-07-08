from pyrogram import Client
import os.path

def GetClient(ClientName: str, id: int | str | None = None, hash: str | None = None):
	client = Client(name=ClientName, api_id=id, api_hash=hash)
	with client:
		for _ in client.get_dialogs(): pass
	return client

def SendFile(app, chat_id, pathfile):
	with app:
		for _ in app.get_dialogs(): pass
		msg = app.send_document(chat_id, rf"{pathfile}")
		return msg.id

def LoadFile(app, chat_id, message_id, outdir='.'):
	with app:
		for _ in app.get_dialogs(): pass
		msg = app.get_messages(chat_id, message_id)
		app.download_media(msg, file_name=os.path.join(outdir, msg.document.file_name))

def CheckChatID(app, chat_id):
	with app:
		for x in app.get_dialogs():
			if str(x.chat.id) == str(chat_id): return True
		return False