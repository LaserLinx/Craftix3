import tkinter as tk
from configparser import ConfigParser
import core.db_engine as db_engine
from tkinter import filedialog
from core.ui import colorschem
import customtkinter as ctk
import os

from core import DataAPI
config = {
	"render3d": False,
	"BorderRender": False,
	"ExportPath": "./exported_data/",
	"mode": "light"
}

def update_settings():
	global config
	db_engine.save_settings(config)

try:
	config = db_engine.load_settings()
except:
	config = {
	"render3d": False,
	"BorderRender": False,
	"ExportPath": "./",
	"mode": "light",
	"them": "default"
	}
	update_settings()
ctk.set_appearance_mode(config.get("mode"))
ctk.set_default_color_theme(os.path.join("./assets/themes",f"{config.get("them")}.json"))




def open(screen):
	global config
	def update_colors(i):
		config["them"] = str(i)
		update_settings()
		DataAPI.update_color()
	def update_them(i):
		if i == "on":
			i = "dark"
		else:
			i = "light"
		config["mode"] = i
		update_settings()
		DataAPI.update_them()	
	def chose_export_path():
		temp_path = config.get("ExportPath")
		path = filedialog.askdirectory()
		if not path == "":
			print(path)
			config["ExportPath"] = str(path)
			update_settings()
		else:
			path = temp_path
			config["ExportPath"] = str(path)
			update_settings()
		export_path_entry.configure(text=config.get("ExportPath"))
		export_path_entry._text=config.get("ExportPath")

	them_mode_var = ctk.StringVar(screen)
	them_mode_ws = ctk.CTkSwitch(screen, text="Light/Dark Mode", command=lambda:update_them(them_mode_var.get()),
								 variable=them_mode_var, onvalue="on", offvalue="off")
	them_mode_ws.pack(side="top",pady=10)
	if config.get("mode") == "light":
		them_mode_ws.deselect()
	else:
		them_mode_ws.select()
	
	them_list = os.listdir("./assets/themes")
	thems = []
	for them in them_list:
		thems.append(str(str(them).replace(".json","")))
	them_selector = ctk.CTkOptionMenu(screen,command=update_colors,values=thems)
	them_selector.pack(side="top",pady=10)
	them_selector.set(config.get("them"))

	export_path_entry = ctk.CTkLabel(screen,width=500,text=config.get("ExportPath"))
	export_path_entry.pack(pady=10)

	export_path_set_button = ctk.CTkButton(screen,command=chose_export_path,text="Chose Floder")
	export_path_set_button.pack(pady=10)
	
	


