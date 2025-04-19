import os
import json
import core.generator as generator
import time
import shutil
import easygui
import requests
import tarfile
from cryptography.fernet import Fernet
database_path = "./database"
projects_path = "./workspaces"
project_name = "test"
key = "LXMOZMksWN6FwFjGHbKDsz8A_wOp5EQoVT6CVJmbUxA="
try:
	with open("Project.active") as f:
		project_name = str(f.read())
		f.close()
except:
	pass



def decrypt_json(encrypted_data, key = key):
	fernet = Fernet(key)
	decrypted_data = fernet.decrypt(encrypted_data).decode()
	return json.loads(decrypted_data)

def encrypt_json(data, key = key):
	json_data = json.dumps(data)
	fernet = Fernet(key)
	encrypted_data = fernet.encrypt(json_data.encode())
	return encrypted_data.decode()

saved_database_name = os.path.join(projects_path,project_name,"database_saved.lsl")
save_path = os.path.join(projects_path,project_name,"save.craftix")
disemble_craft_save_path = os.path.join(projects_path,project_name,"disemble_craft_ids.craftix")
tags_path = os.path.join(projects_path,project_name,"tags.craftix")
tags_backup_path = os.path.join(projects_path,project_name,"tags_backup.craftix")

if not os.path.exists(tags_backup_path):
	with open(tags_backup_path,"w") as f:
		f.write(encrypt_json({"tags": []}))



SERVER_CONNECTION = False
SERVER_URL = "http://192.168.1.101:5000/api"
SERVER_IMAGES_URL = SERVER_URL.replace("/api","")
REFRESH_RATIO = 5.0
USE_SERVER_DATABASE = False


def check_database():
	global database_path
	print("[info] checking database")
	response = requests.post(SERVER_URL,json={"type": "config.json","operation": "get"})
	if response.status_code == 200:
		database = {}
		with open(os.path.join(database_path,"config.json")) as f:
			database = json.loads(f.read()).get("database")
		return database == json.loads(response.json().get("data")).get("database")
	else:
		print(f"[error]: server connection error status code: {response.status_code}")



def download_temp_datas():
	try:
		shutil.rmtree("temp")
	except:
		pass
	try:
		os.mkdir("temp")
	except:
		pass
	image_name = "temp.tar.xz"
	print("downloading images")
	response = requests.get(f"{SERVER_IMAGES_URL}/get_image?name={image_name}")
	if response.status_code == 200:
		with open("temp.tar.xz", "wb") as file:
			file.write(response.content)
		print(f"Image saved to temp.tar.xz")
	else:
		print("downloading images error")
	print("extracting images")
	with tarfile.open(os.path.join("temp.tar.xz"), "r:xz") as tar:
		tar.extractall(path="./temp")
		print("images extraxted")
		print("deleting temp archive")
		try:
			os.remove("temp.tar.xz")
		except:
			pass
		print("temp archive deleted")
	print("downloading database config")
	response = requests.post(SERVER_URL,json={"type": "config.json","operation": "get"})
	if response.status_code == 200:
		with open("temp/config.json","w") as f:
			f.write(json.dumps(json.loads(response.json().get("data"))))
	else:
		print(f"[error]: server connection error status code: {response.status_code}")
	print("database config loaded, starting project")
if os.path.exists(os.path.join(projects_path,project_name,"client.json")):
	SERVER_CONNECTION = True
	with open(os.path.join(projects_path,project_name,"client.json")) as f:
		SERVER_URL = str(json.loads(f.read()).get("url"))
		SERVER_IMAGES_URL = SERVER_URL.replace("/api","")
		if SERVER_CONNECTION:
			if not check_database():
				i = easygui.buttonbox("ERROR\nyou dont have same database as server'\nplease update your database","Database ERROR",choices=["Quit","Use Temp Database"])
				if i == "Use Temp Database":
					download_temp_datas()
					USE_SERVER_DATABASE = True
				else:
					exit(0)




if not SERVER_CONNECTION:
	if not os.path.exists(tags_path):
		try:
			with open(tags_path, "w") as f:
				f.write(encrypt_json({}))
		except Exception as e:
			print(f"Error writing to Project.Active: {e}")
hidec_path = os.path.join(projects_path,project_name,"hidec.craftix")


def save_tags_edits(data,path=tags_path):
	if SERVER_CONNECTION:
		print(["[info]: saving tags into server"])
		response = requests.post(SERVER_URL,json={"type": "tags.craftix","operation": "post","data": str(encrypt_json(data))})
		if response.status_code == 200:
			print("[info] data saved on server")
		else:
			print(f"[error]: connection error status code {response.status_code}")
	else:
		with open(path,"w") as f:
			f.write(encrypt_json(data))
			f.close()

def load_tags_edits(path=tags_path):
	if SERVER_CONNECTION:
		response = requests.post(SERVER_URL,json={"type": "tags.craftix","operation": "get"})
		if response.status_code == 200:
			return decrypt_json(response.json().get("data"))
		else:
			print(f"[error]: server connection error status code: {response.status_code}")
	else:
		with open(path) as f:
			return decrypt_json(f.read())



def load_hidden_crfating_ids(path=hidec_path):
	if SERVER_CONNECTION:
		response = requests.post(SERVER_URL,json={"type": "hidec.craftix","operation": "get"})
		if response.status_code == 200:
			return decrypt_json(response.json().get("data")).get("ids")
		else:
			print(f"[error]: server connection error status code: {response.status_code}")
	else:
		data = {}
		with open(path,"r") as f:
			data = decrypt_json(f.read())
			f.close()
		return data.get("ids")

def save_hidden_crfating_ids(ids=[],path=hidec_path):
	if SERVER_CONNECTION:
		print(["[info]: saving tags into server"])
		data = {}
		data["ids"] = ids
		response = requests.post(SERVER_URL,json={"type": "hidec.craftix","operation": "post","data": str(encrypt_json(data))})
		if response.status_code == 200:
			print("[info] data saved on server")
		else:
			print(f"[error]: connection error status code {response.status_code}")
	else:
		data = {}
		data["ids"] = ids
		with open(path,"w") as f:
			f.write(encrypt_json(data))
			f.close()

def getall(database_path = database_path):
	if USE_SERVER_DATABASE:
		database = {}
		with open(os.path.join("temp","config.json")) as f:
			database = json.loads(f.read())
		tags = database.get("tags")
		database = database.get("database")
		items = database
		items_database = []
		for item in items:
			items_database.append(f"{item.get("mod")}:{item.get("name")}")
			
		with open(os.path.join(database_path,"config.json")) as f:
			tags = json.loads(f.read()).get("tags")
		for tag in tags:
			items_database.append(f"tag:{tag}")
		return items_database
		
	else:
		database = {}
		with open(os.path.join(database_path,"config.json")) as f:
			database = json.loads(f.read()).get("database")
		items = database
		items_database = []
		for item in items:
			items_database.append(f"{item.get("mod")}:{item.get("name")}")
		tags = []
		with open(os.path.join(database_path,"config.json")) as f:
			tags = json.loads(f.read()).get("tags")
		for tag in tags:
			items_database.append(f"tag:{tag}")
		return items_database

def savedatabase(items,name=saved_database_name):
	if SERVER_CONNECTION:
		print(["[info]: saving data into server"])
		data = {}
		data["items"] = items
		response = requests.post(SERVER_URL,json={"type": "database_saved.lsl","operation": "post","data": str(json.dumps(data))})
		if response.status_code == 200:
			print("[info] data saved on server")
		else:
			print(f"[error]: connection error status code {response.status_code}")
	else:
		try:
			with open(name,"w") as f:
				data = {}
				data["items"] = items
				f.write(json.dumps(data))
				f.close()
		except:
			pass
def loaddatabase(name=saved_database_name):
	if SERVER_CONNECTION:
		response = requests.post(SERVER_URL,json={"type": "database_saved.lsl","operation": "get"})
		if response.status_code == 200:
			return json.loads(response.json().get("data")).get("items")
		else:
			print(f"[error]: connection error status code {response.status_code}")
	else:
		try:
			with open(name,"r") as f:
				data = json.loads(f.read())
				items = data.get("items")
				f.close()
			return items
		except:
			pass



def search_path(name, database_path=database_path, tag=False):
	# Record start time
	start_time = time.time()
	#print(f".. searching - {name}, tag: {tag}")
	database = {}
	if USE_SERVER_DATABASE:
		with open(os.path.join("temp","config.json")) as f:
			database = json.loads(f.read()).get("database")
	else:
		with open(os.path.join(database_path,"config.json")) as f:
			database = json.loads(f.read()).get("database")
	
	if tag:
		
		result = os.path.join("./assets","textures","tag.png")
		# Record end time and calculate search time
		end_time = time.time()
		search_time = (end_time - start_time) * 1000  # Convert to milliseconds
		print(f"Found: {result} in {search_time:.2f} ms")
		return result
	else:
		if USE_SERVER_DATABASE:
			try:
				
				results = os.path.join("temp",database[name].get("png"))
				end_time = time.time()
				search_time = (end_time - start_time) * 1000
				#print(f"Found: {results} in {search_time:.2f} ms")
				return results
			except:
				#print(f"No result found for {name}")
				return None
		else:
			try:
				for item in database:
					if item.get("name_with_mod") == name:
						results = os.path.join(database_path,"images",item.get("png"))
				end_time = time.time()
				search_time = (end_time - start_time) * 1000
				#print(f"Found: {results} in {search_time:.2f} ms")
				return results
			except:
				print(f"No result found for {name}")
				return None



#crafting save--
def save_crafting(crafting_data,name,path = save_path):
	if SERVER_CONNECTION:
		print("[info] saving crafting into server")
		response = requests.post(SERVER_URL,json={"type": "save.craftix","operation": "get"})
		if response.status_code == 200:
			data = decrypt_json(response.json().get("data"))
		else:
			print(f"[error]: connection error status code: {response.status_code}")
			return
		data[name] = crafting_data
		response = requests.post(SERVER_URL,json={"type": "save.craftix","operation": "post","data": str(encrypt_json(data))})
		if response.status_code == 200:
			print("[info] crafting updated")
		else:
			print(f"[error]: connection error status code: {response.status_code}")
			return
	else:
		data = {}
		with open(path,"r") as f:
			data = decrypt_json(f.read())
			f.close()
		data[name] = crafting_data
		with open(path,"w") as f:
			f.write(encrypt_json(data))
			f.close()

def load_crfating(path=save_path):
	if SERVER_CONNECTION:
		response = requests.post(SERVER_URL,json={"type": "save.craftix","operation": "get"})
		if response.status_code == 200:
			data = decrypt_json(response.json().get("data"))
			return data
		else:
			print(f"[error]: connection error status code: {response.status_code}")
			return {}
	else:
		data = {}
		with open(path,"r") as f:
			data = decrypt_json(f.read())
			f.close()
		return data

def update_tags(tags,database_path=database_path):
	database = {}
	with open(os.path.join(database_path,"config.json")) as f:
		database = json.loads(f.read())
	database["tags"] = tags
	with open(os.path.join(database_path,"config.json"),"w") as f:
		f.write(json.dumps(database))
	with open(tags_backup_path,"w") as f:
		f.write(encrypt_json({"tags": tags}))




def getprefix(prefixs = [],database_path = database_path):
	mod_names = os.listdir(database_path)
	items_database = []
	for mod_name in mod_names:
		if not mod_name == "tags":
			mod_name_type = os.path.join(database_path,mod_name)
			item_types = os.listdir(mod_name_type)
			for prefix in prefixs:
				if os.path.exists(os.path.join(mod_name_type,prefix)):
					items = os.listdir(os.path.join(mod_name_type,prefix))
					for item in items:	
						i = item.replace(".png","")
						items_database.append(f"{str(mod_name)}:{i}")
		else:
			if "tags" in prefixs:
				tags_path = os.path.join(database_path,"tags")
				items = os.listdir(tags_path)
				for item in items:
					i = item.replace(".png","")
					items_database.append(f"tag:{i}")

	return items_database


def load_tags(path=database_path):
	tags = []
	with open(os.path.join(database_path,"config.json")) as f:
		tags = json.loads(f.read()).get("tags")
	return tags


def remove_crafting(name,path = save_path):
	if SERVER_CONNECTION:
		print("[info] trying connec to the server")
		response = requests.post(SERVER_URL,json={"type": "save.craftix","operation": "get"})
		if response.status_code == 200:
			data = decrypt_json(response.json().get("data"))
		else:
			print(f"[error]: connection error status code: {response.status_code}")
			return
		try:
			data.pop(name)
		except:
			print("[error]: error in removing")
		response = requests.post(SERVER_URL,json={"type": "save.craftix","operation": "post","data": str(encrypt_json(data))})
		if response.status_code == 200:
			print("[info] crafting updated")
		else:
			print(f"[error]: connection error status code: {response.status_code}")
			return
	else:
		data = {}
		with open(path,"r") as f:
			data = decrypt_json(f.read())
			f.close()
		try:
			data.pop(name)
			with open(path,"w") as f:
				f.write(encrypt_json(data))
				f.close()
			print("[info] crafting be deleted!")
		except:
			print(f"[error] in removing {name}")


def load_removed_crfating_ids(path=disemble_craft_save_path):
	if SERVER_CONNECTION:
		response = requests.post(SERVER_URL,json={"type": "disemble_craft_ids.craftix","operation": "get"})
		if response.status_code == 200:
			data = decrypt_json(response.json().get("data"))
			return data.get("ids")
		else:
			print(f"[error]: connection error status code {response.status_code}")
	else:
		data = {}
		with open(path,"r") as f:
			data = decrypt_json(f.read())
			f.close()
		return data.get("ids")

def save_removed_crfating_ids(path=disemble_craft_save_path,ids=[]):
	if SERVER_CONNECTION:
		print(["[info]: saving tags into server"])
		data = {}
		data["ids"] = ids
		response = requests.post(SERVER_URL,json={"type": "disemble_craft_ids.craftix","operation": "post","data": str(encrypt_json(data))})
		if response.status_code == 200:
			print("[info] data saved on server")
		else:
			print(f"[error]: connection error status code {response.status_code}")
	else:
		data = {}
		data["ids"] = ids
		with open(path,"w") as f:
			f.write(encrypt_json(data))
			f.close()
	

try:
	with open(tags_backup_path) as f:
		update_tags(decrypt_json(f.read()).get("tags"))
except:
	print("loading tags error")



def load_settings():
	with open("settings.json") as f:
		data = json.loads(f.read())
		f.close()
	return data
def save_settings(data):
	with open("settings.json","w") as f:
		f.write(json.dumps(data))		
		f.close()




additional_data = ""

def add_compile_data(data):
	global additional_data
	additional_data += "\n" + str(data)




def export_data(gens,path = "./exported_data"):
	global additional_data
	export_data = ""
	remove_ids = load_removed_crfating_ids()
	
	if remove_ids == [None]:
		remove_ids = []
	def generate_craftings(export_data):
		loop = 0
		crafting = {}
		crafting = load_crfating()
		names = crafting.keys()
		export_data = export_data + "\nServerEvents.recipes(event => {"
		for name in names:
			loop = loop + 1
			data = crafting.get(name)
			type = data.get("type")
			if type == "crafting":
				json_data = generator.generate_minecraft_recipe(data)
			elif type == "mechanical_crafting":
				json_data = generator.generate_minecraft_mechanical_crafting_recipe(data)
			elif type == "furnace":
				json_data = generator.generate_minecraft_furnace(data)
			elif type == "pressing":
				json_data = generator.generate_create_pressing(data)
			elif type == "crafting_shapeless":
				json_data = generator.generate_crafting_shapless(data)
			elif type == "stonecutting":
				json_data = generator.generate_stonecutting(data)
			elif type == "smithing_transform":
				json_data = generator.generate_smithing(data)
			elif type == "Custum Json":
				json_data = generator.generate_custum_json(data)
			elif type == "create_mixing":
				json_data = generator.generate_crate_mixing(data)
			elif type == "create_compacting":
				json_data = generator.generate_create_compacting(data)
			elif type == "create_item_application":
				json_data = generator.generate_create_item_application(data)
			elif type == "create_deployng":
				json_data = generator.generate_create_deployng(data)
			elif type == "create_crushing":
				json_data = generator.generate_create_crushing(data)
			elif type == "create_milling":
				json_data = generator.generate_create_milling(data)
			elif type == "create_cutting":
				json_data = generator.generate_create_cutting(data)
			elif type == "Sequence Assembly":
				json_data = generator.generate_create_sequence_assembly(data)				
			elif type == "Vortex":
				print("[info] skipping vortex script")
			elif type == "create_spouting":
				json_data = generator.generate_create_filling(data)
			else:
				try:
					fn = gens.get(type)
					json_data = fn(data)
				except:
					pass
			try:
				if loop == len(names) and len(remove_ids) == 0:
					export_data = export_data + f"\n\tevent.custom({json_data})"
				else:
					export_data = export_data + f"\n\tevent.custom({json_data})"
			except:
				pass
		export_data = export_data + f"\n{'}'})"
		return export_data
	def remove_craftings(export_data):
		loop = 0
		if not load_removed_crfating_ids() == [None]:
			export_data = export_data + "\nServerEvents.recipes(event => {"
			for id in remove_ids:
				loop = loop + 1
				
				try:
					if len(remove_ids) == loop:
						export_data = export_data + f"\n\tevent.remove({"{"}id: '{id}'{"}"})"
					else:
						export_data = export_data + f"\n\tevent.remove({"{"}id: '{id}'{"}"}),"
				except:
					pass
		export_data = export_data + f"\n{'}'})"
		return export_data
	def add_vortex(export_data):
		vortex = ""
		export_data = export_data + f"\n"
		crafting = {}
		crafting = load_crfating()
		names = crafting.keys()
		for name in names:
			data = crafting.get(name)
			type = data.get("type")
			if type == "Vortex":
				vortex = vortex + generator.generate_vortex(data)
		export_data = export_data + vortex
		return export_data
	def generate_hidec(export_data):
		hidec = load_hidden_crfating_ids()
		export_data = export_data + "\nJEIEvents.hideItems(event => {"
		for i in hidec:
			export_data = export_data + f"\nevent.hide('{i}')"
		export_data = export_data + "\n})"
		return export_data
	
	def generate_tags(export_data):
		export_data += "\nServerEvents.tags('item', event => {"
		tags_json = {}
		tags_json = load_tags_edits()
		tags_keys = tags_json.keys()
		for key in tags_keys:
			arguments = tags_json[key].keys()
			for ar in arguments:
				if ar == "add":
					items = tags_json[key].get("add")
					tag = str(key)
					export_data += f"\n\tevent.add('{tag}',{items})"
				elif ar == "remove":
					items = tags_json[key].get("remove")
					tag = str(key)
					export_data += f"\n\tevent.remove('{tag}',{items})"
				elif ar == "rm":
					items = tags_json[key].get("rm")
					tag = str(key)
					export_data += f"\n\tevent.remove('{tag}',{items})"
		
		export_data += "\n})"
		return export_data
	
		
	print("[info]: generating craftings")
	export_data = generate_craftings(export_data)
	print("[info]: generating scripts")
	#export_data = add_vortex(export_data)
	print("[info]: generating deleted craftings")
	export_data = remove_craftings(export_data)
	#export_data = generate_hidec(export_data)
	print("[info]: generating edited tags")
	export_data = generate_tags(export_data)
	export_data += additional_data
	print("Success! generating Done")
	with open(os.path.join(path,"data.js"),"w") as f:
		f.write(export_data)
		f.close()





