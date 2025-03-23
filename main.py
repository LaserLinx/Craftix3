import os
import shutil
import tkinter as tk
from tkinter import messagebox, ttk
import subprocess
import json
import sys
import easygui
from cryptography.fernet import Fernet
from core.ui import colorschem

outline_collor = colorschem.outline_collor
dark_bg_color = colorschem.dark_bg_color
light_bg_color = colorschem.light_bg_color
text_color = colorschem.text_color

DATABASE = "./database"

if not os.path.exists(os.path.join(DATABASE,"config.json")) or not os.path.exists(os.path.join(DATABASE,"images")):
	choice = easygui.buttonbox("ERROR\nInvalid Database Format","Databse Error",choices=["Exit","Repair"])
	if choice == "Repair":
		print("Starting Database Repair...")
		img_paths = []
		database_data = {}
		database_data["database"] = {}
		database_data["tags"] = []
		database_mods = os.listdir(DATABASE)
		print(f"adding: {database_mods}")
		for mod in database_mods:
			if not mod == "tags":
				types = os.listdir(os.path.join(DATABASE,mod))
				print(f"adding {types}")
				for tp in types:
					items = os.listdir(os.path.join(DATABASE,mod,tp))
					for item in items:
						print(item)
						name = item.replace(".png","")
						print(name)
						database_data["database"][name] = {"png": str(item),"mod": str(mod),"type": str(tp)}
						img_paths.append(os.path.join(DATABASE,mod,tp,item))
						print(img_paths)
			
		with open(os.path.join(DATABASE,"config.json"),"w") as f:
			f.write(json.dumps(database_data))
		print("creating images dir")
		os.mkdir(os.path.join(DATABASE,"images"))
		print("moving images")
		for img in img_paths:
			print(f"moving {img}")
			try:
				shutil.move(img,os.path.join(DATABASE,"images"))
			except:
				pass
		
		print("removing old floders")
		for file in os.listdir(DATABASE):
			if not file in ["images","config.json"]:
				try:
					shutil.rmtree(os.path.join(DATABASE,file))
				except:
					pass
		easygui.msgbox("Database repair is Done!")
	else:
		exit(0)

def open_project(project_name):
	try:
		with open("Project.active", "w") as f:
			f.write(str(project_name))
	except Exception as e:
		print(f"Error writing to Project.Active: {e}")
	
	run()

def delete_project(project_name):
	result = messagebox.askyesno("Delete Project", f"Are you sure you want to delete the project '{project_name}'?")
	if result:
		shutil.rmtree(os.path.join('workspaces', project_name))
		load_projects()
key = "LXMOZMksWN6FwFjGHbKDsz8A_wOp5EQoVT6CVJmbUxA="
def encrypt_json(data, key = key):
    json_data = json.dumps(data)
    fernet = Fernet(key)
    encrypted_data = fernet.encrypt(json_data.encode())
    return encrypted_data.decode()

def add_project():
	project_type = easygui.choicebox("Choice Project Type",choices=["Local Project","Server Project"])
	if project_type == "Local Project":
		name = easygui.enterbox("Write Project Name","Create Project")
		os.mkdir(os.path.join("./workspaces/",str(name)))
		saved_database_name = os.path.join("./workspaces/",name,"database_saved.lsl")
		save_path = os.path.join("./workspaces/",name,"save.craftix")
		tags_path = os.path.join("./workspaces/",name,"tags.craftix")
		disemble_craft_save_path = os.path.join("./workspaces/",name,"disemble_craft_ids.craftix")
		hidec_path = os.path.join("./workspaces",name,"hidec.craftix")
		try:
			with open(saved_database_name, "w") as f:
				f.write(json.dumps({"items": []}))
		except Exception as e:
			print(f"Error writing to Project.Active: {e}")	
		try:
			with open(save_path, "w") as f:
				f.write(encrypt_json({}))
		except Exception as e:
			print(f"Error writing to Project.Active: {e}")
		try:
			with open(tags_path, "w") as f:
				f.write(encrypt_json({}))
		except Exception as e:
			print(f"Error writing to Project.Active: {e}")
		try:
			with open(disemble_craft_save_path, "w") as f:
				f.write(encrypt_json({"ids": []}))
		except Exception as e:
			print(f"Error writing to Project.Active: {e}")
		
		try:
			with open(hidec_path, "w") as f:
				f.write(encrypt_json({"ids": []}))
		except Exception as e:
			print(f"Error writing to Project.Active: {e}")
	elif project_type == "Server Project":
		name = easygui.enterbox("Write Project Name","Create Project")
		url = easygui.enterbox("Write Server http api url")
		os.mkdir(os.path.join("./workspaces/",str(name)))
		project_server_data = os.path.join("./workspaces/",name,"client.json")
		try:
			with open(project_server_data, "w") as f:
				f.write(json.dumps({"url": str(url)}))
		except Exception as e:
			print(f"Error writing to Project.Active: {e}")

	load_projects()

def load_projects():
	for widget in project_frame.winfo_children():
		widget.destroy()

	project_dirs = [d for d in os.listdir('workspaces') if os.path.isdir(os.path.join('workspaces', d))]
		
	for project_name in project_dirs:
		frame = tk.Frame(project_frame,background=dark_bg_color,highlightbackground=outline_collor,highlightcolor=outline_collor,highlightthickness=1)
		frame.pack(fill=tk.X, padx=5, pady=5)

		label = tk.Label(frame, text=project_name, anchor="w",background=dark_bg_color,foreground=text_color)
		label.pack(side=tk.LEFT, fill=tk.X, expand=True)

		open_btn = tk.Button(frame, text="Open", command=lambda p=project_name: open_project(p),background=dark_bg_color,activebackground=dark_bg_color,foreground=text_color,activeforeground=text_color,highlightbackground=outline_collor,highlightcolor=outline_collor,highlightthickness=1)
		open_btn.pack(side=tk.RIGHT)

		delete_btn = tk.Button(frame, text="Delete", command=lambda p=project_name: delete_project(p),background=dark_bg_color,activebackground=dark_bg_color,foreground=text_color,activeforeground=text_color,highlightbackground=outline_collor,highlightcolor=outline_collor,highlightthickness=1)
		delete_btn.pack(side=tk.RIGHT)

def run():
	try:
		subprocess.Popen([sys.executable, "craftix.py"])
		print("starting...")
	except Exception as e:
		print(f"Error running main.py: {e}")
	finally:
		root.quit()
		




root = tk.Tk()
#ico = Image.open('./textures/icon.png')
#photo = ImageTk.PhotoImage(ico)
#root.wm_iconphoto(False, photo)
root.title("Craftix Project Manager")
root.config(background=dark_bg_color)
canvas = tk.Canvas(root,background=dark_bg_color,highlightbackground=outline_collor,highlightcolor=outline_collor,highlightthickness=1)
scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
scrollable_frame = ttk.Frame(canvas)

scrollable_frame.bind(
	"<Configure>",
	lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

project_frame = tk.Frame(scrollable_frame,background=dark_bg_color)
project_frame.pack(fill=tk.BOTH, expand=True)


add_project_button = tk.Button(root, text="Add Project", command=add_project,background=light_bg_color,activebackground=dark_bg_color,foreground=text_color,activeforeground=text_color,highlightbackground=outline_collor,highlightcolor=outline_collor,highlightthickness=1)
add_project_button.pack(pady=10)


canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

load_projects()

root.mainloop()
