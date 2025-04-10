import tkinter as tk
from PIL import Image,ImageTk
import core.db_engine as db_engine
from core import centerlib
import core.ui.easydialog as easydialog
import core.ui.settings as settings
from tkinter import simpledialog
from core.graphics import render3d
from core.graphics import border_render
import json
from customtkinter import CTkImage
from core import DataAPI
from collections import OrderedDict
import platform
from core.ui import colorschem
import string
import random
import os
import customtkinter as ctk
ctk.set_appearance_mode(settings.config.get("mode"))
ctk.set_default_color_theme(os.path.join("./assets/themes",f"{settings.config.get("them")}.json"))

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
	return ''.join(random.choice(chars) for _ in range(size))

def get_widget_by_name_in_inv(widget_name):
	"""Vrátí objekt widgetu podle jeho názvu."""
	return globals().get(widget_name, None)
DataAPI.set_get_global_func_in_inv(get_widget_by_name_in_inv)

outline_collor = colorschem.outline_collor
dark_bg_color = colorschem.dark_bg_color
light_bg_color = colorschem.light_bg_color
text_color = colorschem.text_color

def adjust_dpi_scale(root, root_resolution):
	# Získání aktuálního rozlišení obrazovky
	screen_width = root.winfo_screenwidth()	
	screen_height = root.winfo_screenheight()

	# Rozlišování mezi Windows a Linux pro různé škálovací faktory pro widgety
	if platform.system() == "Windows":
		scale_factor = 1.2  # Menší škálování pro Windows
		font_scale_factor = 1.2	  # Vyšší škálování pro písmo na Windows
	else:
		scale_factor = 1.0  # Normální škálování pro Linux
		font_scale_factor = 1.0  # Vyšší škálování pro písmo na Linuxu

	# Výpočet škálovacího faktoru na základě poměru rozlišení
	scale_factor_x = screen_width / root_resolution[0]
	scale_factor_y = screen_height / root_resolution[1]
	scale_factor_dynamic = min(scale_factor_x, scale_factor_y)  # Zvol nejmenší faktor pro konzistentní škálování

	# Aplikace jemného škálování podle manuálně nastaveného faktoru
	scale_factor = min(scale_factor_dynamic, scale_factor)  # Ujisti se, že nebude větší než dynamický faktor

	# Aplikace měřítka na widgety
	root.tk.call('tk', 'scaling', scale_factor)

	# Nastavení velikosti písma podle font_scale_factor
	default_font_size = int(10 * font_scale_factor)  # Používáme jiný faktor pro písmo
	root.option_add("*Font", f"Arial {default_font_size}")


inv_screen=None
saved_palet_database = db_engine.loaddatabase("saveddatabase.xdplou59xturbomax96rp823max5")
def update_palet(palet,items):
	palet.delete(0,tk.END)
	for item in items:
		palet.insert(tk.END,item)

def update_main_palet(db):
	global palet, database
	database = db
	palet.delete(0,tk.END)
	for i in db:
		palet.insert(tk.END,i)

def search(item,database):
	try:
		item = item.lower()
		results = []
		for i in database:
			if item in i:
				results.append(i)
		return results
	except:
		return []
def remove_item(palet):
	saved_palet_database = db_engine.loaddatabase()
	items = saved_palet_database
	for i in palet.curselection():
		item = palet.get(i)
	try:
		items.remove(item)
	except:
		pass
	db_engine.savedatabase(items)
	saved_palet_database = db_engine.loaddatabase()
	update_palet(palet,saved_palet_database)



def add_item(palet,saved_palet):
	saved_palet_database = db_engine.loaddatabase()
	for i in palet.curselection():
		item = palet.get(i)
	saved_palet_database.append(item)
	db_engine.savedatabase(saved_palet_database)
	update_palet(saved_palet,saved_palet_database)


def update_filter(block_filter,item_filter,fluid_filter,tags_filter,palet):
	global database
	block_filter = block_filter.get()
	item_filter = item_filter.get()
	fluid_filter = fluid_filter.get()
	tags_filter = tags_filter.get()
	filters = []
	
	if not block_filter == 0:
		filters.append("block")
	if not item_filter == 0:
		filters.append("item")
	if not fluid_filter == 0:
		filters.append("fluid")
	if not tags_filter == 0:
		filters.append("tags")
	database = db_engine.getprefix(filters)
	
	update_palet(palet,database)
	

latest_item = ""
def load_item(palet):
	global latest_item
	latest_item = get_selected_item()
	
	selection = palet.curselection()
	if selection:
		
		index = selection[0]
		selected_item = palet.get(index)
		minecraft_selected_item = selected_item
		tag = False
		if str(minecraft_selected_item).startswith("tag:"):
			tag = True
		item = db_engine.search_path(selected_item,tag=tag)
		if settings.config.get("render3d") == True:
			
			blocks = db_engine.getprefix(["block"])
			if minecraft_selected_item in blocks:
				render3d.draw_3d_block(item,"3drender.png")
				item = "./3drender.png"

		Image_ = Image.open(item)
		resized_image = Image_.resize((180, 180), resample=0)  # nebo Image.NEAREST

		I_preview_item = CTkImage(light_image=resized_image, size=(180, 180))

		preview_item.configure(image=I_preview_item)
		preview_item.image = I_preview_item
		
		
	else:
		pass


class shortcut():
	def __init__(self,widget):
		self.widget = widget
		self.widget.bind("<Control-a>",self.select_all)
	
	def select_all(self,event):
			event.widget.select_range(0, ctk.END)
			event.widget.icursor(ctk.END)
			return "break"



DataScructures = {
	"crafting": {
		"crafting": {},
		"result_count": 1,
		"result": ""
	},
	"crafting_shapeless": {
		"result": "",
		"crafting": {},
		"result_count": 1
	},
	"furnace": {
		"cookingtime": "200",
		"experience": "0.1",
		"in": "",
		"result": "",
		"result_count": "1",
		"furnace_type": "minecraft:smelting"
	},
	"pressing": {
		"results": [{"item": "","count": 1,"chance": 100}],
		"in": ""
	},
	"stonecutting": {
		"result": "",
		"in": "",
		"result_count": 1
	},
	"smithing_transform": {
		"result": "",
		"in": "",
		"inpatern": "",
		"addition": ""
	},
	"Custum Json": {
		"json": {}
	},
	"create_mixing": {
		"ins_items": {1: "",2: "",3: "",4: "",5: "",6: "",7: "",8: "",9: ""},
		"ins_items_count": {1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1, 8: 1, 9: 1},
		"ins_fluid1": "",
		"ins_fluid2": "",
		"results_items": {1: "",2: "",3: "",4: "",5: "",6: "",7: "",8: "",9: ""},
		"results_items_count": {1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1, 8: 1, 9: 1},
		"results_items_chance": {1: 100, 2: 100, 3: 100, 4: 100, 5: 100, 6: 100, 7: 100, 8: 100, 9: 100},
		"results_fluids1": "",
		"results_fluids2": "",
		"fluids_parms": {1: "1000",2: "1000",3: "1000",4: "100",5: "1000",6: "100"},
		"hated": "None"
	},
	"create_compacting": {
		"ins_items": {1: "",2: "",3: "",4: "",5: "",6: "",7: "",8: "",9: ""},
		"ins_items_count": {1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1, 8: 1, 9: 1},
		"ins_fluid1": "",
		"ins_fluid2": "",
		"results_items": {1: "",2: "",3: "",4: "",5: "",6: "",7: "",8: "",9: ""},
		"results_items_count": {1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1, 8: 1, 9: 1},
		"results_items_chance": {1: 100, 2: 100, 3: 100, 4: 100, 5: 100, 6: 100, 7: 100, 8: 100, 9: 100},
		"results_fluids1": "",
		"results_fluids2": "",
		"fluids_parms": {1: "1000",2: "1000",3: "1000",4: "100",5: "1000",6: "100"},
		"hated": "None"
	},
	"create_item_application": {
		"in": "",
		"sub_in": "",
		"results": [{"item": "","count": 1,"chance": 100}],
		"consument": "1"
	},
	"create_deployng": {
		"in": "",
		"sub_in": "",
		"results": [{"item": "","count": 1,"chance": 100}],
		"consument": "1"
	},
	"create_crushing": {
		"results": [{"item": "","count": 1,"chance": 100}],
		"in": "",
		"time": 1
	},
	"create_milling": {
		"results": [{"item": "","count": 1,"chance": 100}],
		"in": "",
		"time": 1
	},
	"create_cutting": {
		"results": [{"item": "","count": 1,"chance": 100}],
		"in": "",
		"time": 1
	},
	"Vortex": {
		"vortex": ""
	},
	"Sequence Assembly": {
		"results": [{"item": "","count": 1,"chance": 100}],
		"in": "",
		"transitionalItem": "",
		"sequence": {},
		"loops": 1
	},
	"create_spouting": {
		"results": [{"item": "","count": 1,"chance": 100}],
		"in": "",
		"subin": "",
		"amount": 1
	}

}


def AddIntoDataScructures(type,Scructure):
	global DataScructures
	DataScructures[type] = {}
	DataScructures[type] = Scructure

crafting = {}
def create_crafting_palet(type,name,load_function,clb):
	global crafting, DataScructures
	save_crafting()
	crafting = {}
	
	
	if type in ["crafting","mechanical_crafting"]:
		crafting = DataScructures.get("crafting")
	elif type == "crafting_shapeless":
		crafting = DataScructures.get("crafting_shapeless")
	elif type == "furnace":
		crafting = DataScructures.get("furnace")
	elif type == "pressing":
		crafting = DataScructures.get("pressing")
	elif type == "stonecutting":
		crafting = DataScructures.get("stonecutting")
	elif type == "smithing_transform":
		crafting = DataScructures.get("smithing_transform")
	elif type == "Custum Json":
		crafting = DataScructures.get("Custum Json")
	elif type == "create_mixing":
		crafting = DataScructures.get("create_mixing")
	elif type == "create_compacting":
		crafting = DataScructures.get("create_compacting")
	elif type == "create_item_application":
		crafting = DataScructures.get("create_item_application")
	elif type == "create_deployng":
		crafting = DataScructures.get("create_deployng")
	elif type == "create_crushing":
		crafting = DataScructures.get("create_crushing")
	elif type == "create_milling":
		crafting = DataScructures.get("create_milling")
	elif type == "create_cutting":
		crafting = DataScructures.get("create_cutting")
	elif type == "Vortex":
		crafting = DataScructures.get("Vortex")
	elif type == "Sequence Assembly":
		crafting = DataScructures.get("Sequence Assembly")
	elif type == "create_spouting":
		crafting = DataScructures.get("create_spouting")
	else:
		try:
			crafting = DataScructures.get(str(type))
		except:
			pass

	crafting["type"] = str(type)
	crafting["name"] = str(name)
	save_crafting()
	clb()
	load_function(name)

#TODO: add crafting tamplate

	
def create_crafting_result_count(count):
	crafting["result_count"] = count
	print(crafting)

def create_name(name):
	crafting["name"] = str(name)
	print(crafting)


def get_selected_item():
	global crafting
	global palet
	global latest_item
	global saved_palet
	try:
		selection = palet.curselection()
		if selection:
			index = selection[0]
			selected_item = palet.get(index)
			return selected_item
		

		else:
			selection = saved_palet.curselection()
			if selection:
				index = selection[0]
				selected_item = saved_palet.get(index)
				return selected_item
			else:
				
				return latest_item
	except:
		pass


def remove_mod(selected_item):
	return str(selected_item)
	if ":" in selected_item:
		remove_index = ""
					
		for index in selected_item:
			if not index == ":":
				remove_index = str(remove_index) + str(index)
			else:
				remove_index = str(remove_index) + ":"
				break
		return selected_item.replace(remove_index,"")

def furnace_parms(cooking_time = "200",experience = "0.1",result_count = "1"):
	crafting["cookingtime"] = str(cooking_time)
	crafting["experience"] = str(experience)
	crafting["result_count"] = str(result_count)
	print(crafting)
def update_furnace_type(type):
	crafting["furnace_type"] = type
	print(crafting)




def create_crafting(button,crafting_index):
	global crafting
	global palet
	global saved_palet
	try:
		selected_minecraft_item = get_selected_item()
		selected_item = selected_minecraft_item
		if crafting.get("type") in ["crafting","mechanical_crafting"]:
			if not selected_minecraft_item == None:

				selected_item = remove_mod(selected_minecraft_item)
					
				if crafting_index == "result":
					crafting["result"] = str(selected_minecraft_item)

				else:
					crafting["crafting"][str(crafting_index)] = str(selected_minecraft_item)
				print(crafting)
				tag = False
				if str(selected_minecraft_item).startswith("tag:"):
					tag = True
				if settings.config.get("BorderRender") == True:
					preview_image_button = border_render.generate_border(db_engine.search_path(selected_item,tag=tag))
				else:
					preview_image_button = ImageTk.PhotoImage(Image.open(db_engine.search_path(selected_item,tag=tag)).resize((54,54),resample=0))
				button.configure(image=preview_image_button)
				button.image = preview_image_button
			else:
				if crafting_index == "result":
					try:
						crafting.pop("result")
					except:
						pass
				else:
					try:
						crafting["crafting"].pop(crafting_index)
					except:
						try:
							crafting["crafting"].pop(str(crafting_index))
						except:
							pass
				print(crafting)
				if settings.config.get("BorderRender") == True:
					preview_image_button = border_render.generate_border("./assets/textures/slot00.png")
				else:
					preview_image_button = ImageTk.PhotoImage(Image.open("./assets/textures/slot00.png").resize((54,54),resample=0))
				button.config(image=preview_image_button)
				button.image = preview_image_button
		elif crafting.get("type") == "crafting_shapeless":
			if not selected_minecraft_item == None:

				selected_item = remove_mod(selected_minecraft_item)
					
				if crafting_index == "result":
					crafting["result"] = str(selected_minecraft_item)

				else:
					crafting["crafting"][str(crafting_index)] = str(selected_minecraft_item)
				print(crafting)
				tag = False
				if str(selected_minecraft_item).startswith("tag:"):
					tag = True
				if settings.config.get("BorderRender") == True:
					preview_image_button = border_render.generate_border(db_engine.search_path(selected_item,tag=tag))
				else:
					preview_image_button = ImageTk.PhotoImage(Image.open(db_engine.search_path(selected_item,tag=tag)).resize((54,54),resample=0))
				button.config(image=preview_image_button)
				button.image = preview_image_button
			else:
				if crafting_index == "result":
					try:
						crafting.pop("result")
					except:
						pass
				else:
					try:
						crafting["crafting"].pop(crafting_index)
					except:
						try:
							crafting["crafting"].pop(str(crafting_index))
						except:
							pass
				print(crafting)
				if settings.config.get("BorderRender") == True:
					preview_image_button = border_render.generate_border("./assets/textures/slot00.png")
				else:
					preview_image_button = ImageTk.PhotoImage(Image.open("./assets/textures/slot00.png").resize((54,54),resample=0))
				button.config(image=preview_image_button)
				button.image = preview_image_button
		elif crafting.get("type") == "furnace":
			if not selected_minecraft_item == None:
				selected_item = remove_mod(selected_minecraft_item)
				if crafting_index == "in":
					crafting["in"] = selected_minecraft_item
					tag = False
					if str(selected_minecraft_item).startswith("tag:"):
						tag = True
					if settings.config.get("BorderRender") == True:
						preview_image_button = border_render.generate_border(db_engine.search_path(selected_item,tag=tag))
					else:
						preview_image_button = ImageTk.PhotoImage(Image.open(db_engine.search_path(selected_item,tag=tag)).resize((54,54),resample=0))
					button.config(image=preview_image_button)
					button.image = preview_image_button
					print(crafting)
				if crafting_index == "result":
					crafting["result"] = selected_minecraft_item
					tag = False
					if str(selected_minecraft_item).startswith("tag:"):
						tag = True
					if settings.config.get("BorderRender") == True:
						preview_image_button = border_render.generate_border(db_engine.search_path(selected_item,tag=tag))
					else:
						preview_image_button = ImageTk.PhotoImage(Image.open(db_engine.search_path(selected_item,tag=tag)).resize((54,54),resample=0))
					button.config(image=preview_image_button)
					button.image = preview_image_button
					print(crafting)
			else:
				try:
					if crafting_index == "result":
						crafting.pop("result")
					elif crafting_index == "in":
						crafting.pop("in")
					if settings.config.get("BorderRender") == True:
						preview_image_button = border_render.generate_border("./assets/textures/slot00.png")
					else:
						preview_image_button = ImageTk.PhotoImage(Image.open("./assets/textures/slot00.png").resize((54,54),resample=0))
					button.config(image=preview_image_button)
					button.image = preview_image_button
					print(crafting)
				except:
					pass

		elif crafting.get("type") == "pressing":
			
			if not selected_minecraft_item == None:
				selected_item = remove_mod(selected_minecraft_item)
				if crafting_index == "in":
					crafting["in"] = selected_minecraft_item
					tag = False
					if str(selected_minecraft_item).startswith("tag:"):
						tag = True
					if settings.config.get("BorderRender") == True:
						preview_image_button = border_render.generate_border(db_engine.search_path(selected_item,tag=tag))
					else:
						preview_image_button = ImageTk.PhotoImage(Image.open(db_engine.search_path(selected_item,tag=tag)).resize((54,54),resample=0))
					button.config(image=preview_image_button)
					button.image = preview_image_button
					print(crafting)
			else:
				try:
					
					if crafting_index == "in":
						crafting.pop("in")
					if settings.config.get("BorderRender") == True:
						preview_image_button = border_render.generate_border("./assets/textures/slot00.png")
					else:
						preview_image_button = ImageTk.PhotoImage(Image.open("./assets/textures/slot00.png").resize((54,54),resample=0))
					button.config(image=preview_image_button)
					button.image = preview_image_button
					print(crafting)
				except:
					pass
		elif crafting.get("type") == "stonecutting":
			if not selected_minecraft_item == None:
				try:
					selected_item = remove_mod(selected_minecraft_item)
					if crafting_index == "in":
						crafting["in"] = selected_minecraft_item
						tag = False
						if str(selected_minecraft_item).startswith("tag:"):
							tag = True
						if settings.config.get("BorderRender") == True:
							preview_image_button = border_render.generate_border(db_engine.search_path(selected_item,tag=tag))
						else:
							preview_image_button = ImageTk.PhotoImage(Image.open(db_engine.search_path(selected_item,tag=tag)).resize((54,54),resample=0))
						button.config(image=preview_image_button)
						button.image = preview_image_button
						print(crafting)
					if crafting_index == "result":
						crafting["result"] = selected_minecraft_item
						tag = False
						if str(selected_minecraft_item).startswith("tag:"):
							tag = True
						if settings.config.get("BorderRender") == True:
							preview_image_button = border_render.generate_border(db_engine.search_path(selected_item,tag=tag))
						else:
							preview_image_button = ImageTk.PhotoImage(Image.open(db_engine.search_path(selected_item,tag=tag)).resize((54,54),resample=0))
						button.config(image=preview_image_button)
						button.image = preview_image_button
						print(crafting)
				except:
					pass
			else:
				try:
					if crafting_index == "result":
						crafting.pop("result")
					elif crafting_index == "in":
						crafting.pop("in")
					if settings.config.get("BorderRender") == True:
						preview_image_button = border_render.generate_border("./assets/textures/slot00.png")
					else:
						preview_image_button = ImageTk.PhotoImage(Image.open("./assets/textures/slot00.png").resize((54,54),resample=0))
					button.config(image=preview_image_button)
					button.image = preview_image_button
					print(crafting)
				except:
					pass
		

		elif crafting.get("type") == "smithing_transform":
			if not selected_minecraft_item == None:
				try:
					selected_item = remove_mod(selected_minecraft_item)
					if crafting_index == "in":
						crafting["in"] = selected_minecraft_item
						tag = False
						if str(selected_minecraft_item).startswith("tag:"):
							tag = True
						if settings.config.get("BorderRender") == True:
							preview_image_button = border_render.generate_border(db_engine.search_path(selected_item,tag=tag))
						else:
							preview_image_button = ImageTk.PhotoImage(Image.open(db_engine.search_path(selected_item,tag=tag)).resize((54,54),resample=0))
						button.config(image=preview_image_button)
						button.image = preview_image_button
						print(crafting)
					if crafting_index == "result":
						crafting["result"] = selected_minecraft_item
						tag = False
						if str(selected_minecraft_item).startswith("tag:"):
							tag = True
						if settings.config.get("BorderRender") == True:
							preview_image_button = border_render.generate_border(db_engine.search_path(selected_item,tag=tag))
						else:
							preview_image_button = ImageTk.PhotoImage(Image.open(db_engine.search_path(selected_item,tag=tag)).resize((54,54),resample=0))
						button.config(image=preview_image_button)
						button.image = preview_image_button
						print(crafting)

					if crafting_index == "inpatern":
						crafting["inpatern"] = selected_minecraft_item
						tag = False
						if str(selected_minecraft_item).startswith("tag:"):
							tag = True
						if settings.config.get("BorderRender") == True:
							preview_image_button = border_render.generate_border(db_engine.search_path(selected_item,tag=tag))
						else:
							preview_image_button = ImageTk.PhotoImage(Image.open(db_engine.search_path(selected_item,tag=tag)).resize((54,54),resample=0))
						button.config(image=preview_image_button)
						button.image = preview_image_button
						print(crafting)
					if crafting_index == "addition":
						crafting["addition"] = selected_minecraft_item
						tag = False
						if str(selected_minecraft_item).startswith("tag:"):
							tag = True
						if settings.config.get("BorderRender") == True:
							preview_image_button = border_render.generate_border(db_engine.search_path(selected_item,tag=tag))
						else:
							preview_image_button = ImageTk.PhotoImage(Image.open(db_engine.search_path(selected_item,tag=tag)).resize((54,54),resample=0))
						button.config(image=preview_image_button)
						button.image = preview_image_button
						print(crafting)
				except:
					pass

			else:
				try:
					if crafting_index == "result":
						crafting.pop("result")
					elif crafting_index == "in":
						crafting.pop("in")
					elif crafting_index == "inpatern":
						crafting.pop("inpatern")
					elif crafting_index == "addition":
						crafting.pop("addition")
					if settings.config.get("BorderRender") == True:
						preview_image_button = border_render.generate_border("./assets/textures/slot00.png")
					else:
						preview_image_button = ImageTk.PhotoImage(Image.open("./assets/textures/slot00.png").resize((54,54),resample=0))
					button.config(image=preview_image_button)
					button.image = preview_image_button
					print(crafting)
				except:
					pass

		elif crafting.get("type") == "create_crushing":
			
			if not selected_minecraft_item == None:
				selected_item = remove_mod(selected_minecraft_item)
				if crafting_index == "in":
					crafting["in"] = selected_minecraft_item
					tag = False
					if str(selected_minecraft_item).startswith("tag:"):
						tag = True
					if settings.config.get("BorderRender") == True:
						preview_image_button = border_render.generate_border(db_engine.search_path(selected_item,tag=tag))
					else:
						preview_image_button = ImageTk.PhotoImage(Image.open(db_engine.search_path(selected_item,tag=tag)).resize((54,54),resample=0))
					button.config(image=preview_image_button)
					button.image = preview_image_button
					print(crafting)
			else:
				try:
					
					if crafting_index == "in":
						crafting.pop("in")
					if settings.config.get("BorderRender") == True:
						preview_image_button = border_render.generate_border("./assets/textures/slot00.png")
					else:
						preview_image_button = ImageTk.PhotoImage(Image.open("./assets/textures/slot00.png").resize((54,54),resample=0))
					button.config(image=preview_image_button)
					button.image = preview_image_button
					print(crafting)
				except:
					pass

		elif crafting.get("type") == "create_milling":
			
			if not selected_minecraft_item == None:
				selected_item = remove_mod(selected_minecraft_item)
				if crafting_index == "in":
					crafting["in"] = selected_minecraft_item
					tag = False
					if str(selected_minecraft_item).startswith("tag:"):
						tag = True
					if settings.config.get("BorderRender") == True:
						preview_image_button = border_render.generate_border(db_engine.search_path(selected_item,tag=tag))
					else:
						preview_image_button = ImageTk.PhotoImage(Image.open(db_engine.search_path(selected_item,tag=tag)).resize((54,54),resample=0))
					button.config(image=preview_image_button)
					button.image = preview_image_button
					print(crafting)
			else:
				try:
					
					if crafting_index == "in":
						crafting.pop("in")
					if settings.config.get("BorderRender") == True:
						preview_image_button = border_render.generate_border("./assets/textures/slot00.png")
					else:
						preview_image_button = ImageTk.PhotoImage(Image.open("./assets/textures/slot00.png").resize((54,54),resample=0))
					button.config(image=preview_image_button)
					button.image = preview_image_button
					print(crafting)
				except:
					pass

		elif crafting.get("type") == "create_cutting":
			
			if not selected_minecraft_item == None:
				selected_item = remove_mod(selected_minecraft_item)
				if crafting_index == "in":
					crafting["in"] = selected_minecraft_item
					tag = False
					if str(selected_minecraft_item).startswith("tag:"):
						tag = True
					if settings.config.get("BorderRender") == True:
						preview_image_button = border_render.generate_border(db_engine.search_path(selected_item,tag=tag))
					else:
						preview_image_button = ImageTk.PhotoImage(Image.open(db_engine.search_path(selected_item,tag=tag)).resize((54,54),resample=0))
					button.config(image=preview_image_button)
					button.image = preview_image_button
					print(crafting)
			else:
				try:
					
					if crafting_index == "in":
						crafting.pop("in")
					if settings.config.get("BorderRender") == True:
						preview_image_button = border_render.generate_border("./assets/textures/slot00.png")
					else:
						preview_image_button = ImageTk.PhotoImage(Image.open("./assets/textures/slot00.png").resize((54,54),resample=0))
					button.config(image=preview_image_button)
					button.image = preview_image_button
					print(crafting)
				except:
					pass
		elif crafting.get("type") == "Sequence Assembly":
			
			if not selected_minecraft_item == None:
				selected_item = remove_mod(selected_minecraft_item)
				if crafting_index == "in":
					crafting["in"] = selected_minecraft_item
					tag = False
					if str(selected_minecraft_item).startswith("tag:"):
						tag = True
					if settings.config.get("BorderRender") == True:
						preview_image_button = border_render.generate_border(db_engine.search_path(selected_item,tag=tag))
					else:
						preview_image_button = ImageTk.PhotoImage(Image.open(db_engine.search_path(selected_item,tag=tag)).resize((54,54),resample=0))
					button.config(image=preview_image_button)
					button.image = preview_image_button
					print(crafting)
				elif crafting_index == "transitionalItem":
					crafting["transitionalItem"] = selected_minecraft_item
					tag = False
					if str(selected_minecraft_item).startswith("tag:"):
						tag = True
					if settings.config.get("BorderRender") == True:
						preview_image_button = border_render.generate_border(db_engine.search_path(selected_item,tag=tag))
					else:
						preview_image_button = ImageTk.PhotoImage(Image.open(db_engine.search_path(selected_item,tag=tag)).resize((54,54),resample=0))
					button.config(image=preview_image_button)
					button.image = preview_image_button
					print(crafting)
			else:
				try:
					
					if crafting_index == "in":
						crafting.pop("in")
					elif crafting_index == "transitionalItem":
						crafting.pop("transitionalItem")
					if settings.config.get("BorderRender") == True:
						preview_image_button = border_render.generate_border("./assets/textures/slot00.png")
					else:
						preview_image_button = ImageTk.PhotoImage(Image.open("./assets/textures/slot00.png").resize((54,54),resample=0))
					button.config(image=preview_image_button)
					button.image = preview_image_button
					print(crafting)
				except:
					pass
		
		elif crafting.get("type") == "create_spouting":
			
			if not selected_minecraft_item == None:
				selected_item = remove_mod(selected_minecraft_item)
				if crafting_index == "in":
					crafting["in"] = selected_minecraft_item
					tag = False
					if str(selected_minecraft_item).startswith("tag:"):
						tag = True
					if settings.config.get("BorderRender") == True:
						preview_image_button = border_render.generate_border(db_engine.search_path(selected_item,tag=tag))
					else:
						preview_image_button = ImageTk.PhotoImage(Image.open(db_engine.search_path(selected_item,tag=tag)).resize((54,54),resample=0))
					button.config(image=preview_image_button)
					button.image = preview_image_button
					print(crafting)
				if crafting_index == "subin":
					crafting["subin"] = selected_minecraft_item
					tag = False
					if str(selected_minecraft_item).startswith("tag:"):
						tag = True
					if settings.config.get("BorderRender") == True:
						preview_image_button = border_render.generate_border(db_engine.search_path(selected_item,tag=tag))
					else:
						preview_image_button = ImageTk.PhotoImage(Image.open(db_engine.search_path(selected_item,tag=tag)).resize((54,54),resample=0))
					button.config(image=preview_image_button)
					button.image = preview_image_button
					print(crafting)
			else:
				try:
					
					if crafting_index == "in":
						crafting.pop("in")
					if settings.config.get("BorderRender") == True:
						preview_image_button = border_render.generate_border("./assets/textures/slot00.png")
					else:
						preview_image_button = ImageTk.PhotoImage(Image.open("./assets/textures/slot00.png").resize((54,54),resample=0))
					button.config(image=preview_image_button)
					button.image = preview_image_button
					print(crafting)
					if crafting_index == "subin":
						crafting.pop("subin")
					if settings.config.get("BorderRender") == True:
						preview_image_button = border_render.generate_border("./assets/textures/slot00.png")
					else:
						preview_image_button = ImageTk.PhotoImage(Image.open("./assets/textures/slot00.png").resize((54,54),resample=0))
					button.config(image=preview_image_button)
					button.image = preview_image_button
					print(crafting)
				except:
					pass
	except:
		pass
#TODO: adding functions on click buttons


def export(gens):
	db_engine.export_data(gens,path=str(settings.config.get("ExportPath")))



def remove_crfating(name):
	db_engine.remove_crafting(name)
	global crafting
	crafting = {}


buttons_element = []

def arsenal_add(arsenal,seq):
	try:
		selection = arsenal.curselection()
		if selection:
			index = selection[0]
			selected_item = arsenal.get(index)
			iid = str(id_generator(50))
			seq.insert(tk.END,f"{selected_item}                                                                  id:{iid}")
			data_templates = {
				"pressing": {"type": "pressing"},
				"cutting": {"type": "cutting","processtime": 1},
				"deployng": {"type": "deployng","subitem": "","ussage": True},
				"spouting": {"type": "spouting","fluid": "","amount": 1000}
			}
			crafting["sequence"][iid] = data_templates.get(selected_item)
		else:
			print("[info] any item selected in arsenal menu skiping..")
	except:
		print("[error] error in geting selected item from arsenal menu")


def clear_ctk_frames(frame):
	try:
		for widget in frame.winfo_children():
			if isinstance(widget, ctk.CTkFrame):
				widget.destroy()
	except:
		pass

def update_parm_frame(editor,element,frame):
	global crafting
	try:
		selection = element.curselection()
		if selection:
			index = selection[0]
			selected_item = element.get(index)
			editor.delete("0.0",tk.END)
			steps_list = crafting["sequence"].keys()
			for step in steps_list:
				if f"id:{step}" in str(selected_item):
					clear_ctk_frames(frame)
					if crafting["sequence"][step].get("type") == "deployng":
						editor.place(x=5,y=200)
						edit_space = ctk.CTkFrame(frame,width=415,height=161)
						edit_space.place(x=1,y=1)
						def update_subitem(step):
							selected_minecraft_item = get_selected_item()
							selected_item = selected_minecraft_item
							if not selected_minecraft_item == None:
								selected_item = remove_mod(selected_minecraft_item)
								crafting["sequence"][step]["subitem"] = selected_minecraft_item															
								tag = False
								if str(selected_minecraft_item).startswith("tag:"):
									tag = True
								if settings.config.get("BorderRender") == True:
									preview_image_button = border_render.generate_border(db_engine.search_path(selected_item,tag=tag))
								else:
									preview_image_button = ImageTk.PhotoImage(Image.open(db_engine.search_path(selected_item,tag=tag)).resize((54,54),resample=0))
								slot00.config(image=preview_image_button)
								slot00.image = preview_image_button
								print(crafting)
						slot00 = tk.Button(edit_space,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda st=step: update_subitem(st),highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color)
						slot00.pack(side="left",padx=10,pady=10)
						if crafting["sequence"][step].get("subitem") == "":
							pass
						else:
							selected_minecraft_item = crafting["sequence"][step].get("subitem")
							selected_item_p = remove_mod(selected_minecraft_item)
							tag = False
							if str(selected_minecraft_item).startswith("tag:"):
								tag = True
							if settings.config.get("BorderRender") == True:
								preview_image_button = border_render.generate_border(db_engine.search_path(selected_item_p,tag=tag))
							else:
								preview_image_button = ImageTk.PhotoImage(Image.open(db_engine.search_path(selected_item_p,tag=tag)).resize((54,54),resample=0))
							slot00.config(image=preview_image_button)
							slot00.image = preview_image_button
						def update_ussage(step):
							crafting["sequence"][step]["ussage"] = consument_value.get()
						consument_value = tk.BooleanVar(edit_space,crafting["sequence"][step].get("ussage"))
						block_checkbox1 = ctk.CTkCheckBox(edit_space,text="Consume Item",command=lambda st=step: update_ussage(st),variable=consument_value,onvalue=True,offvalue=False)
						block_checkbox1.pack(side="left",pady=10,padx=10)

					elif crafting["sequence"][step].get("type") == "spouting":
						editor.place(x=5,y=200)
						edit_space = ctk.CTkFrame(frame,width=415,height=161)
						edit_space.place(x=1,y=1)
						def update_subitem(step):
							selected_minecraft_item = get_selected_item()
							selected_item = selected_minecraft_item
							if not selected_minecraft_item == None:
								selected_item = remove_mod(selected_minecraft_item)
								crafting["sequence"][step]["fluid"] = selected_minecraft_item															
								tag = False
								if str(selected_minecraft_item).startswith("tag:"):
									tag = True
								if settings.config.get("BorderRender") == True:
									preview_image_button = border_render.generate_border(db_engine.search_path(selected_item,tag=tag))
								else:
									preview_image_button = ImageTk.PhotoImage(Image.open(db_engine.search_path(selected_item,tag=tag)).resize((54,54),resample=0))
								slot00.config(image=preview_image_button)
								slot00.image = preview_image_button
								print(crafting)
						slot00 = tk.Button(edit_space,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda st=step: update_subitem(st),highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color)
						slot00.pack(side="left",padx=10,pady=10)
						if crafting["sequence"][step].get("fluid") == "":
							pass
						else:
							selected_minecraft_item = crafting["sequence"][step].get("fluid")
							selected_item_p = remove_mod(selected_minecraft_item)
							tag = False
							if str(selected_minecraft_item).startswith("tag:"):
								tag = True
							if settings.config.get("BorderRender") == True:
								preview_image_button = border_render.generate_border(db_engine.search_path(selected_item_p,tag=tag))
							else:
								preview_image_button = ImageTk.PhotoImage(Image.open(db_engine.search_path(selected_item_p,tag=tag)).resize((54,54),resample=0))
							slot00.config(image=preview_image_button)
							slot00.image = preview_image_button
						#--
						def update_amount(step):
							crafting["sequence"][step]["amount"] = int(block_checkbox1.get())
						block_checkbox1 = ctk.CTkEntry(edit_space)
						block_checkbox1.pack(side="left",pady=10,padx=10)
						block_checkbox1.bind("<KeyRelease>",lambda e, st=step:update_amount(st))
						block_checkbox1.insert(0,crafting["sequence"][step].get("amount"))

					elif crafting["sequence"][step].get("type") == "cutting":
						editor.place(x=5,y=200)
						edit_space = ctk.CTkFrame(frame,width=415,height=161)
						edit_space.place(x=1,y=1)
						def update_amount(step):
							crafting["sequence"][step]["processtime"] = int(block_checkbox1.get())
						block_checkbox1 = ctk.CTkEntry(edit_space)
						block_checkbox1.pack(side="left",pady=10,padx=10)
						block_checkbox1.bind("<KeyRelease>",lambda e, st=step:update_amount(st))
						block_checkbox1.insert(0,crafting["sequence"][step].get("processtime"))
					else:
						clear_ctk_frames(frame)
						
						editor.insert(tk.END,json.dumps(crafting["sequence"].get(step),indent=4))
		else:
			print("[info] any item selected in arsenal menu skiping..")
	except:
		print("[error] error in geting selected item from arsenal menu")

def update_parms(element,editor):
	try:
		selection = element.curselection()
		if selection:
			index = selection[0]
			selected_item = element.get(index)
			steps_list = crafting["sequence"].keys()
			for step in steps_list:
				if f"id:{step}" in str(selected_item):
					crafting["sequence"][step] = json.loads(editor)
					print(crafting)
		else:
			print("[info] any item selected in arsenal menu skiping..")
	except:
		print("[error] error in geting selected item from arsenal menu")


def arsenal_remove(arsenal):
	try:
		selection = arsenal.curselection()
		if selection:
			index = selection[0]
			selected_item = arsenal.get(index)
			print(selected_item)
			arsenal.delete(index)
			steps_list = crafting["sequence"].keys()
			for step in steps_list:
				if f"id:{step}" in str(selected_item):
					crafting["sequence"].pop(step)
		else:
			print("[info] any item selected in arsenal menu skiping..")
	except:
		print("[error] error in geting selected item from arsenal menu")

def save_crafting(entry=None):
	if not entry == "":
		name = crafting.get("name")
		print(name)
		if not name == None:
			db_engine.save_crafting(crafting,name)
		else:
			pass

def load_crafting(load_item,buttons,recipe_name_entry):
	global crafting, buttons_element
	buttons_element = buttons
	saved_crafting_database = db_engine.load_crfating()
	if not load_item == None:
		item_crafting_data = saved_crafting_database.get(load_item)
		print(item_crafting_data)
		if item_crafting_data.get("type") == "crafting":
			recipe_name_entry.delete(0,tk.END)
			recipe_name_entry.insert(0,item_crafting_data.get("name"))
			buttons[10].delete(0,tk.END)
		
			buttons[10].insert(0,item_crafting_data.get("result_count"))
			crafting = item_crafting_data
			for place in item_crafting_data["crafting"].keys():
				item = item_crafting_data["crafting"].get(place)
				
				selected_item = item
				if ":" in selected_item:
					remove_index = ""
					
					for index in selected_item:
						if not index == ":":
							remove_index = str(remove_index) + str(index)
						else:
							remove_index = str(remove_index) + ":"
							break

					item = item.replace(remove_index,"")
				tag = False
				if str(selected_item).startswith("tag:"):
					tag = True
				if settings.config.get("BorderRender") == True:
					image = ImageTk.PhotoImage(Image.open(border_render.generate_border(db_engine.search_path(item,tag=tag)),resample=0))
				else:
					image = ImageTk.PhotoImage(Image.open(db_engine.search_path(item,tag=tag)).resize((54,54),resample=0))
				buttons[int(place) - 1].config(image=image)
				buttons[int(place) - 1].image = image
			item = item_crafting_data.get("result")
			selected_item = item
			if ":" in selected_item:
				remove_index = ""
				for index in selected_item:
					if not index == ":":
						remove_index = str(remove_index) + str(index)
					else:
						remove_index = str(remove_index) + ":"
						break

				item = item.replace(remove_index,"")
				
			try:
				tag = False
				if str(selected_item).startswith("tag:"):
					tag = True
				if settings.config.get("BorderRender") == True:
					image = ImageTk.PhotoImage(Image.open(border_render.generate_border(db_engine.search_path(item,tag=tag)),resample=0))
				else:
					image = ImageTk.PhotoImage(Image.open(db_engine.search_path(item,tag=tag)).resize((54,54),resample=0))				
				buttons[9].config(image=image)
				buttons[9].image = image	
			except:
				pass
		elif item_crafting_data.get("type") == "mechanical_crafting":
			recipe_name_entry.delete(0,tk.END)
			recipe_name_entry.insert(0,item_crafting_data.get("name"))
			buttons[82].delete(0,tk.END)
			buttons[82].insert(0,item_crafting_data.get("result_count"))
			crafting = item_crafting_data
			for place in item_crafting_data["crafting"].keys():
				item = item_crafting_data["crafting"].get(place)
				
				selected_item = item
				item = remove_mod(selected_item)
				tag = False
				if str(selected_item).startswith("tag:"):
					tag = True
				if settings.config.get("BorderRender") == True:
					image = ImageTk.PhotoImage(Image.open(border_render.generate_border(db_engine.search_path(item,tag=tag)),resample=0))
				else:
					image = ImageTk.PhotoImage(Image.open(db_engine.search_path(item,tag=tag)).resize((54,54),resample=0))
				buttons[int(place) - 1].config(image=image)
				buttons[int(place) - 1].image = image
			item = item_crafting_data.get("result")
			selected_item = item
			item = remove_mod(selected_item)
				
			try:
				tag = False
				if str(selected_item).startswith("tag:"):
					tag = True
				if settings.config.get("BorderRender") == True:
					image = ImageTk.PhotoImage(Image.open(border_render.generate_border(db_engine.search_path(item,tag=tag)),resample=0))
				else:
					image = ImageTk.PhotoImage(Image.open(db_engine.search_path(item,tag=tag)).resize((54,54),resample=0))
				buttons[81].config(image=image)
				buttons[81].image = image	
			except:
				pass
		elif item_crafting_data.get("type") == "furnace":
			crafting = item_crafting_data
			recipe_name_entry.delete(0,tk.END)
			recipe_name_entry.insert(0,item_crafting_data.get("name"))
			buttons[2].delete(0,tk.END)
			buttons[2].insert(0,item_crafting_data.get("cookingtime"))
			buttons[3].delete(0,tk.END)
			buttons[3].insert(0,item_crafting_data.get("experience"))
			buttons[4].delete(0,tk.END)
			buttons[4].insert(0,item_crafting_data.get("result_count"))
			item = remove_mod(item_crafting_data.get("in"))
			selected_item = item_crafting_data.get("in")
			tag = False
			if str(selected_item).startswith("tag:"):
				tag = True
			if settings.config.get("BorderRender") == True:
				image = ImageTk.PhotoImage(Image.open(border_render.generate_border(db_engine.search_path(item,tag=tag)),resample=0))
			else:
				image = ImageTk.PhotoImage(Image.open(db_engine.search_path(item,tag=tag)).resize((54,54),resample=0))
			buttons[0].config(image=image)
			buttons[0].image = image
			item = remove_mod(item_crafting_data.get("result"))
			selected_item = item_crafting_data.get("result")
			tag = False
			if str(selected_item).startswith("tag:"):
				tag = True
			if settings.config.get("BorderRender") == True:
				image = ImageTk.PhotoImage(Image.open(border_render.generate_border(db_engine.search_path(item,tag=tag)),resample=0))
			else:
				image = ImageTk.PhotoImage(Image.open(db_engine.search_path(item,tag=tag)).resize((54,54),resample=0))
			buttons[1].config(image=image)
			buttons[1].image = image
			buttons[5].set(item_crafting_data.get("furnace_type"))
		elif item_crafting_data.get("type") == "pressing":
			crafting = item_crafting_data
			print(crafting)
			recipe_name_entry.delete(0,tk.END)
			recipe_name_entry.insert(0,item_crafting_data.get("name"))
			item = remove_mod(item_crafting_data.get("in"))
			tag = False
			if str(item).startswith("tag:"):
				tag = True
			if settings.config.get("BorderRender") == True:
				image = ImageTk.PhotoImage(Image.open(border_render.generate_border(db_engine.search_path(item,tag=tag)),resample=0))
			else:
				image = ImageTk.PhotoImage(Image.open(db_engine.search_path(item,tag=tag)).resize((54,54),resample=0))
			buttons[0].config(image=image)
			buttons[0].image=image
			for i in list(range(5,len(crafting.get("results")) + 5)):
				item = remove_mod(buttons[i].result.get("item"))
				if not item == None:
					tag = False
					if str(item).startswith("tag:"):
						tag = True
					if settings.config.get("BorderRender") == True:
						image = ImageTk.PhotoImage(Image.open(border_render.generate_border(db_engine.search_path(item,tag=tag)),resample=0))
					else:
						image = ImageTk.PhotoImage(Image.open(db_engine.search_path(item,tag=tag)).resize((54,54),resample=0))
					buttons[i].config(image=image)
					buttons[i].image=image

		elif item_crafting_data.get("type") == "crafting_shapeless":
			recipe_name_entry.delete(0,tk.END)
			recipe_name_entry.insert(0,item_crafting_data.get("name"))
			buttons[10].delete(0,tk.END)
			buttons[10].insert(0,item_crafting_data.get("result_count"))
			crafting = item_crafting_data
			for place in item_crafting_data["crafting"].keys():
				item = item_crafting_data["crafting"].get(place)
				
				selected_item = item
				if ":" in selected_item:
					remove_index = ""
					
					for index in selected_item:
						if not index == ":":
							remove_index = str(remove_index) + str(index)
						else:
							remove_index = str(remove_index) + ":"
							break

					item = item.replace(remove_index,"")
					tag = False
					if str(selected_item).startswith("tag:"):
						tag = True
				if settings.config.get("BorderRender") == True:
					image = ImageTk.PhotoImage(Image.open(border_render.generate_border(db_engine.search_path(item,tag=tag)),resample=0))
				else:
					image = ImageTk.PhotoImage(Image.open(db_engine.search_path(item,tag=tag)).resize((54,54),resample=0))
				buttons[int(place) - 1].config(image=image)
				buttons[int(place) - 1].image = image
			item = item_crafting_data.get("result")
			selected_item = item
			if ":" in selected_item:
				remove_index = ""
				for index in selected_item:
					if not index == ":":
						remove_index = str(remove_index) + str(index)
					else:
						remove_index = str(remove_index) + ":"
						break

				item = item.replace(remove_index,"")
				
			try:
				tag = False
				if str(selected_item).startswith("tag:"):
					tag = True
				if settings.config.get("BorderRender") == True:
					image = ImageTk.PhotoImage(Image.open(border_render.generate_border(db_engine.search_path(item,tag=tag)),resample=0))
				else:
					image = ImageTk.PhotoImage(Image.open(db_engine.search_path(item,tag=tag)).resize((54,54),resample=0))				
				buttons[9].config(image=image)
				buttons[9].image = image	
			except:
				pass
		elif item_crafting_data.get("type") == "stonecutting":
			recipe_name_entry.delete(0,tk.END)
			recipe_name_entry.insert(0,item_crafting_data.get("name"))
			buttons[2].delete(0,tk.END)
			buttons[2].insert(0,item_crafting_data.get("result_count"))
			crafting = item_crafting_data
			try:
				selected_item = crafting.get("in")
				item = remove_mod(selected_item)
				tag = False
				if str(selected_item).startswith("tag:"):
					tag = True
				if settings.config.get("BorderRender") == True:
					image = ImageTk.PhotoImage(Image.open(border_render.generate_border(db_engine.search_path(item,tag=tag)),resample=0))
				else:
					image = ImageTk.PhotoImage(Image.open(db_engine.search_path(item,tag=tag)).resize((54,54),resample=0))
				buttons[0].config(image=image)
				buttons[0].image = image
			except:
				pass
			try:
				selected_item = crafting.get("result")
				item = remove_mod(selected_item)
				tag = False
				if str(selected_item).startswith("tag:"):
					tag = True
				if settings.config.get("BorderRender") == True:
					image = ImageTk.PhotoImage(Image.open(border_render.generate_border(db_engine.search_path(item,tag=tag)),resample=0))
				else:
					image = ImageTk.PhotoImage(Image.open(db_engine.search_path(item,tag=tag)).resize((54,54),resample=0))
				buttons[1].config(image=image)
				buttons[1].image = image
			except:
				pass
		
		elif item_crafting_data.get("type") == "smithing_transform":
			recipe_name_entry.delete(0,tk.END)
			recipe_name_entry.insert(0,item_crafting_data.get("name"))

			crafting = item_crafting_data
			try:
				selected_item = crafting.get("in")
				item = remove_mod(selected_item)
				tag = False
				if str(selected_item).startswith("tag:"):
					tag = True
				if settings.config.get("BorderRender") == True:
					image = ImageTk.PhotoImage(Image.open(border_render.generate_border(db_engine.search_path(item,tag=tag)),resample=0))
				else:
					image = ImageTk.PhotoImage(Image.open(db_engine.search_path(item,tag=tag)).resize((54,54),resample=0))
				buttons[0].config(image=image)
				buttons[0].image = image
			except:
				pass
			try:
				selected_item = crafting.get("result")
				item = remove_mod(selected_item)
				tag = False
				if str(selected_item).startswith("tag:"):
					tag = True
				if settings.config.get("BorderRender") == True:
					image = ImageTk.PhotoImage(Image.open(border_render.generate_border(db_engine.search_path(item,tag=tag)),resample=0))
				else:
					image = ImageTk.PhotoImage(Image.open(db_engine.search_path(item,tag=tag)).resize((54,54),resample=0))
				buttons[1].config(image=image)
				buttons[1].image = image
			except:
				pass
			try:
				selected_item = crafting.get("inpatern")
				item = remove_mod(selected_item)
				tag = False
				if str(selected_item).startswith("tag:"):
					tag = True
				if settings.config.get("BorderRender") == True:
					image = ImageTk.PhotoImage(Image.open(border_render.generate_border(db_engine.search_path(item,tag=tag)),resample=0))
				else:
					image = ImageTk.PhotoImage(Image.open(db_engine.search_path(item,tag=tag)).resize((54,54),resample=0))
				buttons[2].config(image=image)
				buttons[2].image = image
			except:
				pass
			try:
				selected_item = crafting.get("addition")
				item = remove_mod(selected_item)
				tag = False
				if str(selected_item).startswith("tag:"):
					tag = True
				if settings.config.get("BorderRender") == True:
					image = ImageTk.PhotoImage(Image.open(border_render.generate_border(db_engine.search_path(item,tag=tag)),resample=0))
				else:
					image = ImageTk.PhotoImage(Image.open(db_engine.search_path(item,tag=tag)).resize((54,54),resample=0))
				buttons[3].config(image=image)
				buttons[3].image = image
			except:
				pass
			
		elif item_crafting_data.get("type") == "Custum Json":
			recipe_name_entry.delete(0,tk.END)
			recipe_name_entry.insert(0,item_crafting_data.get("name"))
			crafting = item_crafting_data
			buttons[0].delete(1.0,ctk.END)
			buttons[0].insert(1.0,json.dumps(crafting.get("json"),indent="\t"))
		
		elif item_crafting_data.get("type") == "create_mixing":
			recipe_name_entry.delete(0,tk.END)
			recipe_name_entry.insert(0,item_crafting_data.get("name"))
			crafting = item_crafting_data
			#load fluids
			# in fluid 1
			selected_item = crafting.get("ins_fluid1")
			if not selected_item == "":
				item = remove_mod(selected_item)
				tag = False
				if str(selected_item).startswith("tag:"):
					tag = True
				if settings.config.get("BorderRender") == True:
					image = ImageTk.PhotoImage(Image.open(border_render.generate_border(db_engine.search_path(item,tag=tag)),resample=0))
				else:
					image = ImageTk.PhotoImage(Image.open(db_engine.search_path(item,tag=tag)).resize((54,54),resample=0))
				buttons[18].config(image=image)
				buttons[18].image = image
			# in fluid 2
			selected_item = crafting.get("ins_fluid2")
			if not selected_item == "":
				item = remove_mod(selected_item)
				tag = False
				if str(selected_item).startswith("tag:"):
					tag = True
				if settings.config.get("BorderRender") == True:
					image = ImageTk.PhotoImage(Image.open(border_render.generate_border(db_engine.search_path(item,tag=tag)),resample=0))
				else:
					image = ImageTk.PhotoImage(Image.open(db_engine.search_path(item,tag=tag)).resize((54,54),resample=0))
				buttons[19].config(image=image)
				buttons[19].image = image
			# result fluid 1
			selected_item = crafting.get("results_fluids1")
			if not selected_item == "":
				item = remove_mod(selected_item)
				tag = False
				if str(selected_item).startswith("tag:"):
					tag = True
				if settings.config.get("BorderRender") == True:
					image = ImageTk.PhotoImage(Image.open(border_render.generate_border(db_engine.search_path(item,tag=tag)),resample=0))
				else:
					image = ImageTk.PhotoImage(Image.open(db_engine.search_path(item,tag=tag)).resize((54,54),resample=0))
				buttons[20].config(image=image)
				buttons[20].image = image
			# result fluid 2
			selected_item = crafting.get("results_fluids2")
			if not selected_item == "":
				item = remove_mod(selected_item)
				tag = False
				if str(selected_item).startswith("tag:"):
					tag = True
				if settings.config.get("BorderRender") == True:
					image = ImageTk.PhotoImage(Image.open(border_render.generate_border(db_engine.search_path(item,tag=tag)),resample=0))
				else:
					image = ImageTk.PhotoImage(Image.open(db_engine.search_path(item,tag=tag)).resize((54,54),resample=0))
				buttons[21].config(image=image)
				buttons[21].image = image
			#item input load logic
			input_items = crafting.get("ins_items")
			for index in range(0,9):
				selected_item = input_items.get(str(index + 1))
				if not selected_item == "":
					item = remove_mod(selected_item)
					tag = False
					if str(selected_item).startswith("tag:"):
						tag = True
					if settings.config.get("BorderRender") == True:
						image = ImageTk.PhotoImage(Image.open(border_render.generate_border(db_engine.search_path(item,tag=tag)),resample=0))
					else:
						image = ImageTk.PhotoImage(Image.open(db_engine.search_path(item,tag=tag)).resize((54,54),resample=0))
					buttons[index].config(image=image)
					buttons[index].image = image
				

			#item result load logic
			input_items = crafting.get("results_items")
			for index in range(9,18):
				selected_item = input_items.get(str(index - 9 + 1))
				if not selected_item == "":
					item = remove_mod(selected_item)
					tag = False
					if str(selected_item).startswith("tag:"):
						tag = True
					if settings.config.get("BorderRender") == True:
						image = ImageTk.PhotoImage(Image.open(border_render.generate_border(db_engine.search_path(item,tag=tag)),resample=0))
					else:
						image = ImageTk.PhotoImage(Image.open(db_engine.search_path(item,tag=tag)).resize((54,54),resample=0))
					buttons[index].config(image=image)
					buttons[index].image = image
			#item input count load logic
			input_items_count = crafting.get("ins_items_count")
			for index in range(22,31):
				count = input_items_count.get(str(index - 22 + 1))
				buttons[index].delete(0,tk.END)
				buttons[index].insert(0,count)
			input_items_count = crafting.get("results_items_count")
			for index in range(31,40):
				count = input_items_count.get(str(index - 31 + 1))
				buttons[index].delete(0,tk.END)
				buttons[index].insert(0,count)
			input_items_count = crafting.get("results_items_chance")
			for index in range(40,49):
				count = input_items_count.get(str(index - 40 + 1))
				buttons[index].delete(0,tk.END)
				buttons[index].insert(0,count)
			fluids_parms = crafting.get("fluids_parms")
			index = 49
			buttons[index].delete(0,tk.END)
			buttons[index].insert(0,fluids_parms.get("1"))
			index = 50
			buttons[index].delete(0,tk.END)
			buttons[index].insert(0,fluids_parms.get("2"))
			index = 51
			buttons[index].delete(0,tk.END)
			buttons[index].insert(0,fluids_parms.get("3"))
			index = 52
			buttons[index].delete(0,tk.END)
			buttons[index].insert(0,fluids_parms.get("4"))
			index = 53
			buttons[index].delete(0,tk.END)
			buttons[index].insert(0,fluids_parms.get("5"))
			index = 54
			buttons[index].delete(0,tk.END)
			buttons[index].insert(0,fluids_parms.get("6"))
			buttons[55].set(str(crafting.get("hated")))

		elif item_crafting_data.get("type") == "create_compacting":
			recipe_name_entry.delete(0,tk.END)
			recipe_name_entry.insert(0,item_crafting_data.get("name"))
			crafting = item_crafting_data
			#load fluids
			# in fluid 1
			selected_item = crafting.get("ins_fluid1")
			if not selected_item == "":
				item = remove_mod(selected_item)
				tag = False
				if str(selected_item).startswith("tag:"):
					tag = True
				if settings.config.get("BorderRender") == True:
					image = ImageTk.PhotoImage(Image.open(border_render.generate_border(db_engine.search_path(item,tag=tag)),resample=0))
				else:
					image = ImageTk.PhotoImage(Image.open(db_engine.search_path(item,tag=tag)).resize((54,54),resample=0))
				buttons[18].config(image=image)
				buttons[18].image = image
			# in fluid 2
			selected_item = crafting.get("ins_fluid2")
			if not selected_item == "":
				item = remove_mod(selected_item)
				tag = False
				if str(selected_item).startswith("tag:"):
					tag = True
				if settings.config.get("BorderRender") == True:
					image = ImageTk.PhotoImage(Image.open(border_render.generate_border(db_engine.search_path(item,tag=tag)),resample=0))
				else:
					image = ImageTk.PhotoImage(Image.open(db_engine.search_path(item,tag=tag)).resize((54,54),resample=0))
				buttons[19].config(image=image)
				buttons[19].image = image
			# result fluid 1
			selected_item = crafting.get("results_fluids1")
			if not selected_item == "":
				item = remove_mod(selected_item)
				tag = False
				if str(selected_item).startswith("tag:"):
					tag = True
				if settings.config.get("BorderRender") == True:
					image = ImageTk.PhotoImage(Image.open(border_render.generate_border(db_engine.search_path(item,tag=tag)),resample=0))
				else:
					image = ImageTk.PhotoImage(Image.open(db_engine.search_path(item,tag=tag)).resize((54,54),resample=0))
				buttons[20].config(image=image)
				buttons[20].image = image
			# result fluid 2
			selected_item = crafting.get("results_fluids2")
			if not selected_item == "":
				item = remove_mod(selected_item)
				tag = False
				if str(selected_item).startswith("tag:"):
					tag = True
				if settings.config.get("BorderRender") == True:
					image = ImageTk.PhotoImage(Image.open(border_render.generate_border(db_engine.search_path(item,tag=tag)),resample=0))
				else:
					image = ImageTk.PhotoImage(Image.open(db_engine.search_path(item,tag=tag)).resize((54,54),resample=0))
				buttons[21].config(image=image)
				buttons[21].image = image
			#item input load logic
			input_items = crafting.get("ins_items")
			for index in range(0,9):
				selected_item = input_items.get(str(index + 1))
				if not selected_item == "":
					item = remove_mod(selected_item)
					tag = False
					if str(selected_item).startswith("tag:"):
						tag = True
					if settings.config.get("BorderRender") == True:
						image = ImageTk.PhotoImage(Image.open(border_render.generate_border(db_engine.search_path(item,tag=tag)),resample=0))
					else:
						image = ImageTk.PhotoImage(Image.open(db_engine.search_path(item,tag=tag)).resize((54,54),resample=0))
					buttons[index].config(image=image)
					buttons[index].image = image
				

			#item result load logic
			input_items = crafting.get("results_items")
			for index in range(9,18):
				selected_item = input_items.get(str(index - 9 + 1))
				if not selected_item == "":
					item = remove_mod(selected_item)
					tag = False
					if str(selected_item).startswith("tag:"):
						tag = True
					if settings.config.get("BorderRender") == True:
						image = ImageTk.PhotoImage(Image.open(border_render.generate_border(db_engine.search_path(item,tag=tag)),resample=0))
					else:
						image = ImageTk.PhotoImage(Image.open(db_engine.search_path(item,tag=tag)).resize((54,54),resample=0))
					buttons[index].config(image=image)
					buttons[index].image = image
			#item input count load logic
			input_items_count = crafting.get("ins_items_count")
			for index in range(22,31):
				count = input_items_count.get(str(index - 22 + 1))
				buttons[index].delete(0,tk.END)
				buttons[index].insert(0,count)
			input_items_count = crafting.get("results_items_count")
			for index in range(31,40):
				count = input_items_count.get(str(index - 31 + 1))
				buttons[index].delete(0,tk.END)
				buttons[index].insert(0,count)
			input_items_count = crafting.get("results_items_chance")
			for index in range(40,49):
				count = input_items_count.get(str(index - 40 + 1))
				buttons[index].delete(0,tk.END)
				buttons[index].insert(0,count)
			fluids_parms = crafting.get("fluids_parms")
			index = 49
			buttons[index].delete(0,tk.END)
			buttons[index].insert(0,fluids_parms.get("1"))
			index = 50
			buttons[index].delete(0,tk.END)
			buttons[index].insert(0,fluids_parms.get("2"))
			index = 51
			buttons[index].delete(0,tk.END)
			buttons[index].insert(0,fluids_parms.get("3"))
			index = 52
			buttons[index].delete(0,tk.END)
			buttons[index].insert(0,fluids_parms.get("4"))
			index = 53
			buttons[index].delete(0,tk.END)
			buttons[index].insert(0,fluids_parms.get("5"))
			index = 54
			buttons[index].delete(0,tk.END)
			buttons[index].insert(0,fluids_parms.get("6"))
			buttons[55].set(str(crafting.get("hated")))

		elif item_crafting_data.get("type") == "create_item_application":
			recipe_name_entry.delete(0,tk.END)
			recipe_name_entry.insert(0,item_crafting_data.get("name"))
			crafting = item_crafting_data

			selected_item = crafting.get("in")
			if not selected_item == "":
				item = remove_mod(selected_item)
				tag = False
				if str(selected_item).startswith("tag:"):
					tag = True
				if settings.config.get("BorderRender") == True:
					image = ImageTk.PhotoImage(Image.open(border_render.generate_border(db_engine.search_path(item,tag=tag)),resample=0))
				else:
					image = ImageTk.PhotoImage(Image.open(db_engine.search_path(item,tag=tag)).resize((54,54),resample=0))
				buttons[0].config(image=image)
				buttons[0].image = image
			selected_item = crafting.get("sub_in")
			if not selected_item == "":
				item = remove_mod(selected_item)
				tag = False
				if str(selected_item).startswith("tag:"):
					tag = True
				if settings.config.get("BorderRender") == True:
					image = ImageTk.PhotoImage(Image.open(border_render.generate_border(db_engine.search_path(item,tag=tag)),resample=0))
				else:
					image = ImageTk.PhotoImage(Image.open(db_engine.search_path(item,tag=tag)).resize((54,54),resample=0))
				buttons[1].config(image=image)
				buttons[1].image = image

			buttons[6].set(int(crafting.get("consument")))
			
			for i in list(range(8,len(crafting.get("results")) + 8)):
				print(i)
				item = remove_mod(buttons[i].result.get("item"))
				if not item == None:
					tag = False
					if str(selected_item).startswith("tag:"):
						tag = True
					if settings.config.get("BorderRender") == True:
						image = ImageTk.PhotoImage(Image.open(border_render.generate_border(db_engine.search_path(item,tag=tag)),resample=0))
					else:
						image = ImageTk.PhotoImage(Image.open(db_engine.search_path(item,tag=tag)).resize((54,54),resample=0))
					buttons[i].config(image=image)
					buttons[i].image=image

		elif item_crafting_data.get("type") == "create_deployng":
			recipe_name_entry.delete(0,tk.END)
			recipe_name_entry.insert(0,item_crafting_data.get("name"))
			crafting = item_crafting_data

			selected_item = crafting.get("in")
			if not selected_item == "":
				item = remove_mod(selected_item)
				tag = False
				if str(selected_item).startswith("tag:"):
					tag = True
				if settings.config.get("BorderRender") == True:
					image = ImageTk.PhotoImage(Image.open(border_render.generate_border(db_engine.search_path(item,tag=tag)),resample=0))
				else:
					image = ImageTk.PhotoImage(Image.open(db_engine.search_path(item,tag=tag)).resize((54,54),resample=0))
				buttons[0].config(image=image)
				buttons[0].image = image
			selected_item = crafting.get("sub_in")
			if not selected_item == "":
				item = remove_mod(selected_item)
				tag = False
				if str(selected_item).startswith("tag:"):
					tag = True
				if settings.config.get("BorderRender") == True:
					image = ImageTk.PhotoImage(Image.open(border_render.generate_border(db_engine.search_path(item,tag=tag)),resample=0))
				else:
					image = ImageTk.PhotoImage(Image.open(db_engine.search_path(item,tag=tag)).resize((54,54),resample=0))
				buttons[1].config(image=image)
				buttons[1].image = image

			buttons[6].set(int(crafting.get("consument")))
			
			for i in list(range(8,len(crafting.get("results")) + 8)):
				print(i)
				item = remove_mod(buttons[i].result.get("item"))
				if not item == None:
					tag = False
					if str(selected_item).startswith("tag:"):
						tag = True
					if settings.config.get("BorderRender") == True:
						image = ImageTk.PhotoImage(Image.open(border_render.generate_border(db_engine.search_path(item,tag=tag)),resample=0))
					else:
						image = ImageTk.PhotoImage(Image.open(db_engine.search_path(item,tag=tag)).resize((54,54),resample=0))
					buttons[i].config(image=image)
					buttons[i].image=image

		elif item_crafting_data.get("type") == "create_crushing":
			crafting = item_crafting_data
			print(crafting)
			recipe_name_entry.delete(0,tk.END)
			recipe_name_entry.insert(0,item_crafting_data.get("name"))
			item = remove_mod(item_crafting_data.get("in"))
			tag = False
			if str(item).startswith("tag:"):
				tag = True
			if settings.config.get("BorderRender") == True:
				image = ImageTk.PhotoImage(Image.open(border_render.generate_border(db_engine.search_path(item,tag=tag)),resample=0))
			else:
				image = ImageTk.PhotoImage(Image.open(db_engine.search_path(item,tag=tag)).resize((54,54),resample=0))
			buttons[0].config(image=image)
			buttons[0].image=image
			buttons[5].delete(0,tk.END)
			buttons[5].insert(0,crafting.get("time"))
			for i in list(range(7,len(crafting.get("results")) + 7)):
				item = remove_mod(buttons[i].result.get("item"))
				if not item == None:
					tag = False
					if str(item).startswith("tag:"):
						tag = True
					if settings.config.get("BorderRender") == True:
						image = ImageTk.PhotoImage(Image.open(border_render.generate_border(db_engine.search_path(item,tag=tag)),resample=0))
					else:
						image = ImageTk.PhotoImage(Image.open(db_engine.search_path(item,tag=tag)).resize((54,54),resample=0))
					buttons[i].config(image=image)
					buttons[i].image=image

		elif item_crafting_data.get("type") == "create_milling":
			crafting = item_crafting_data
			print(crafting)
			recipe_name_entry.delete(0,tk.END)
			recipe_name_entry.insert(0,item_crafting_data.get("name"))
			item = remove_mod(item_crafting_data.get("in"))
			tag = False
			if str(item).startswith("tag:"):
				tag = True
			if settings.config.get("BorderRender") == True:
				image = ImageTk.PhotoImage(Image.open(border_render.generate_border(db_engine.search_path(item,tag=tag)),resample=0))
			else:
				image = ImageTk.PhotoImage(Image.open(db_engine.search_path(item,tag=tag)).resize((54,54),resample=0))
			buttons[0].config(image=image)
			buttons[0].image=image
			buttons[5].delete(0,tk.END)
			buttons[5].insert(0,crafting.get("time"))
			for i in list(range(7,len(crafting.get("results")) + 7)):
				item = remove_mod(buttons[i].result.get("item"))
				if not item == None:
					tag = False
					if str(item).startswith("tag:"):
						tag = True
					if settings.config.get("BorderRender") == True:
						image = ImageTk.PhotoImage(Image.open(border_render.generate_border(db_engine.search_path(item,tag=tag)),resample=0))
					else:
						image = ImageTk.PhotoImage(Image.open(db_engine.search_path(item,tag=tag)).resize((54,54),resample=0))
					buttons[i].config(image=image)
					buttons[i].image=image
		elif item_crafting_data.get("type") == "create_cutting":
			crafting = item_crafting_data
			print(crafting)
			recipe_name_entry.delete(0,tk.END)
			recipe_name_entry.insert(0,item_crafting_data.get("name"))
			item = remove_mod(item_crafting_data.get("in"))
			tag = False
			if str(item).startswith("tag:"):
				tag = True
			if settings.config.get("BorderRender") == True:
				image = ImageTk.PhotoImage(Image.open(border_render.generate_border(db_engine.search_path(item,tag=tag)),resample=0))
			else:
				image = ImageTk.PhotoImage(Image.open(db_engine.search_path(item,tag=tag)).resize((54,54),resample=0))
			buttons[0].config(image=image)
			buttons[0].image=image
			buttons[5].delete(0,tk.END)
			buttons[5].insert(0,crafting.get("time"))
			for i in list(range(7,len(crafting.get("results")) + 7)):
				item = remove_mod(buttons[i].result.get("item"))
				if not item == None:
					tag = False
					if str(item).startswith("tag:"):
						tag = True
					if settings.config.get("BorderRender") == True:
						image = ImageTk.PhotoImage(Image.open(border_render.generate_border(db_engine.search_path(item,tag=tag)),resample=0))
					else:
						image = ImageTk.PhotoImage(Image.open(db_engine.search_path(item,tag=tag)).resize((54,54),resample=0))
					buttons[i].config(image=image)
					buttons[i].image=image

		elif item_crafting_data.get("type") == "Vortex":
			recipe_name_entry.delete(0,tk.END)
			recipe_name_entry.insert(0,item_crafting_data.get("name"))
			crafting = item_crafting_data
			buttons[0].delete("1.0",tk.END)
			buttons[0].insert("1.0",crafting.get("vortex"))

		elif item_crafting_data.get("type") == "Sequence Assembly":
			crafting = item_crafting_data
			print(crafting)
			recipe_name_entry.delete(0,tk.END)
			recipe_name_entry.insert(0,item_crafting_data.get("name"))
			try:
				item = remove_mod(item_crafting_data.get("in"))
				tag = False
				if str(item).startswith("tag:"):
					tag = True
				if settings.config.get("BorderRender") == True:
					image = ImageTk.PhotoImage(Image.open(border_render.generate_border(db_engine.search_path(item,tag=tag)),resample=0))
				else:
					image = ImageTk.PhotoImage(Image.open(db_engine.search_path(item,tag=tag)).resize((54,54),resample=0))
				buttons[0].config(image=image)
				buttons[0].image=image
			except:
				pass
			try:
				item = remove_mod(item_crafting_data.get("transitionalItem"))
				tag = False
				if str(item).startswith("tag:"):
					tag = True
				if settings.config.get("BorderRender") == True:
					image = ImageTk.PhotoImage(Image.open(border_render.generate_border(db_engine.search_path(item,tag=tag)),resample=0))
				else:
					image = ImageTk.PhotoImage(Image.open(db_engine.search_path(item,tag=tag)).resize((54,54),resample=0))
				buttons[1].config(image=image)
				buttons[1].image=image
			except:
				pass
			buttons[2].delete(0,tk.END)
			buttons[2].insert(0,item_crafting_data.get("loops"))
			data_list = crafting["sequence"].keys()
			for data in data_list:
				buttons[4].insert(tk.END,f"{crafting["sequence"][data].get("type")}                                                                   id:{data}")

			for i in list(range(14,len(crafting.get("results")) + 14)):
				item = remove_mod(buttons[i].result.get("item"))
				if not item == None:
					tag = False
					if str(item).startswith("tag:"):
						tag = True
					if settings.config.get("BorderRender") == True:
						image = ImageTk.PhotoImage(Image.open(border_render.generate_border(db_engine.search_path(item,tag=tag)),resample=0))
					else:
						image = ImageTk.PhotoImage(Image.open(db_engine.search_path(item,tag=tag)).resize((54,54),resample=0))
					buttons[i].config(image=image)
					buttons[i].image=image
		
		elif item_crafting_data.get("type") == "create_spouting":
			crafting = item_crafting_data
			print(crafting)
			recipe_name_entry.delete(0,tk.END)
			recipe_name_entry.insert(0,item_crafting_data.get("name"))
			item = remove_mod(item_crafting_data.get("in"))
			tag = False
			if str(item).startswith("tag:"):
				tag = True
			if settings.config.get("BorderRender") == True:
				image = ImageTk.PhotoImage(Image.open(border_render.generate_border(db_engine.search_path(item,tag=tag)),resample=0))
			else:
				image = ImageTk.PhotoImage(Image.open(db_engine.search_path(item,tag=tag)).resize((54,54),resample=0))
			buttons[0].config(image=image)
			buttons[0].image=image
			item = remove_mod(item_crafting_data.get("subin"))
			tag = False
			if str(item).startswith("tag:"):
				tag = True
			if settings.config.get("BorderRender") == True:
				image = ImageTk.PhotoImage(Image.open(border_render.generate_border(db_engine.search_path(item,tag=tag)),resample=0))
			else:
				image = ImageTk.PhotoImage(Image.open(db_engine.search_path(item,tag=tag)).resize((54,54),resample=0))
			buttons[7].config(image=image)
			buttons[7].image=image
			buttons[5].delete(0,tk.END)
			buttons[5].insert(0,crafting.get("amount"))
			for i in list(range(8,len(crafting.get("results")) + 8)):
				item = remove_mod(buttons[i].result.get("item"))
				if not item == None:
					tag = False
					if str(item).startswith("tag:"):
						tag = True
					if settings.config.get("BorderRender") == True:
						image = ImageTk.PhotoImage(Image.open(border_render.generate_border(db_engine.search_path(item,tag=tag)),resample=0))
					else:
						image = ImageTk.PhotoImage(Image.open(db_engine.search_path(item,tag=tag)).resize((54,54),resample=0))
					buttons[i].config(image=image)
					buttons[i].image=image
		else:
			crafting = item_crafting_data
			recipe_name_entry.delete(0,tk.END)
			recipe_name_entry.insert(0,item_crafting_data.get("name"))

#TODO: load crafting logic


def move_key_up(d, key):
	keys = list(d.keys())		
	if key not in keys or keys.index(key) == 0:
		return d
	index = keys.index(key)
	keys[index], keys[index - 1] = keys[index - 1], keys[index]
	return OrderedDict((k, d[k]) for k in keys)

def move_key_down(d, key):
	keys = list(d.keys())		
	if key not in keys or keys.index(key) == 0:
		return d
	index = keys.index(key)
	keys[index], keys[index + 1] = keys[index + 1], keys[index]
	return OrderedDict((k, d[k]) for k in keys)

def sequence_as_move_up(listbox):
	global crafting
	try:
		selected = listbox.curselection()
		if not selected:
			return
		index = selected[0]
		if index == 0:
			return
			
		text = listbox.get(index)
		sequence = crafting.get("sequence")
		seq_keys = sequence.keys()
		for key in seq_keys:
			if f"id:{key}" in text:
		
				sequence = move_key_up(sequence,key)
		crafting["sequence"]=sequence
		listbox.delete(index)
		listbox.insert(index - 1, text)
		listbox.selection_set(index - 1)
	except:
		pass

def sequence_as_move_down(listbox):
	global crafting
	try:
		selected = listbox.curselection()
		if not selected:
			return
		index = selected[0]
		if index == 0:
			return
			
		text = listbox.get(index)
		sequence = crafting.get("sequence")
		seq_keys = sequence.keys()
		for key in seq_keys:
			if f"id:{key}" in text:
		
				sequence = move_key_down(sequence,key)
		crafting["sequence"]=sequence
		listbox.delete(index)
		listbox.insert(index + 1, text)
		listbox.selection_set(index + 1)
	except:
		pass

def create_item_application_updates(id,element):
	item = get_selected_item()
	if not item == None:
		crafting[id] = str(item)
		selected_item = crafting.get(id)
		item = remove_mod(selected_item)
		tag = False
		if str(selected_item).startswith("tag:"):
			tag = True
		if settings.config.get("BorderRender") == True:
			image = border_render.generate_border(db_engine.search_path(item,tag=tag))
		else:
			image = ImageTk.PhotoImage(Image.open(db_engine.search_path(item,tag=tag)).resize((54,54),resample=0))
		element.config(image=image)
		element.image = image
	else:
		crafting[id] = ""
		try:
			if settings.config.get("BorderRender") == True:
				preview_image_button = border_render.generate_border("./assets/textures/slot00.png")
			else:
				preview_image_button = ImageTk.PhotoImage(Image.open("./assets/textures/slot00.png").resize((54,54),resample=0))
			element.config(image=preview_image_button)
			element.image = preview_image_button
			print(crafting)
		except:
			pass




def update_mixing_hate(val):
	crafting["hated"] = str(val)

def set_mixing_ins_counts(count,index):
	crafting["ins_items_count"][index] = count
	print(crafting)


def set_mixing_results_counts(count,index):
	crafting["results_items_count"][index] = count
	print(crafting)

def set_mixing_results_chance(count,index):
	crafting["results_items_chance"][index] = count
	print(crafting)

def set_fluids_parms(id,count):
	crafting["fluids_parms"][id] = count
	print(crafting)

def set_mixing_fluids(button,index):
	fluid = get_selected_item()
	if not fluid == None:
		crafting[index] = str(fluid)
		selected_item = crafting.get(index)
		item = remove_mod(selected_item)
		tag = False
		if str(selected_item).startswith("tag:"):
			tag = True
		if settings.config.get("BorderRender") == True:
			image = border_render.generate_border(db_engine.search_path(item,tag=tag))
		else:
			image = ImageTk.PhotoImage(Image.open(db_engine.search_path(item,tag=tag)).resize((54,54),resample=0))
		button.config(image=image)
		button.image = image
	else:
		crafting[index] = ""
		try:
			if settings.config.get("BorderRender") == True:
				preview_image_button = border_render.generate_border("./assets/textures/slot00.png")
			else:
				preview_image_button = ImageTk.PhotoImage(Image.open("./assets/textures/slot00.png").resize((54,54),resample=0))
			button.config(image=preview_image_button)
			button.image = preview_image_button
			print(crafting)
		except:
			pass


def set_mixing_items_ins(button,index):
	fluid = get_selected_item()
	if not fluid == None:
		crafting["ins_items"][index] = str(fluid)
		selected_item = crafting["ins_items"].get(index)
		item = remove_mod(selected_item)
		tag = False
		if str(selected_item).startswith("tag:"):
			tag = True
		if settings.config.get("BorderRender") == True:
			image = border_render.generate_border(db_engine.search_path(item,tag=tag))
		else:
			image = ImageTk.PhotoImage(Image.open(db_engine.search_path(item,tag=tag)).resize((54,54),resample=0))
		button.config(image=image)
		button.image = image
	else:
		crafting["ins_items"][index] = ""
		try:
			if settings.config.get("BorderRender") == True:
				preview_image_button = border_render.generate_border("./assets/textures/slot00.png")
			else:
				preview_image_button = ImageTk.PhotoImage(Image.open("./assets/textures/slot00.png").resize((54,54),resample=0))
			button.config(image=preview_image_button)
			button.image = preview_image_button
			print(crafting)
		except:
			pass

def set_mixing_items_results(button,index):
	fluid = get_selected_item()
	if not fluid == None:
		crafting["results_items"][index] = str(fluid)
		selected_item = crafting["results_items"].get(index)
		item = remove_mod(selected_item)
		tag = False
		if str(selected_item).startswith("tag:"):
			tag = True
		if settings.config.get("BorderRender") == True:
			image = border_render.generate_border(db_engine.search_path(item,tag=tag))
		else:
			image = ImageTk.PhotoImage(Image.open(db_engine.search_path(item,tag=tag)).resize((54,54),resample=0))
		button.config(image=image)
		button.image = image
	else:
		crafting["results_items"][index] = ""
		try:
			if settings.config.get("BorderRender") == True:
				preview_image_button = border_render.generate_border("./assets/textures/slot00.png")
			else:
				preview_image_button = ImageTk.PhotoImage(Image.open("./assets/textures/slot00.png").resize((54,54),resample=0))
			button.config(image=preview_image_button)
			button.image = preview_image_button
			print(crafting)
		except:
			pass


def set_result_pressing_count(vl,callback):
	result = callback.result
	item = result.get("item")
	chance = result.get("chance")
	crafting["results"].remove(result)
	result = {"item": item,"count": vl.get(),"chance":chance}
	callback.result = result
	crafting["results"].append(result)
	print(crafting)
def set_result_pressing_chance(vl,callback):
	result =  callback.result
	item = result.get("item")
	count = result.get("count")
	crafting["results"].remove(result)
	print(crafting)
	result = {"item": item,"chance": vl.get(),"count":count}
	callback.result = result
	crafting["results"].append(result)
	print(crafting)

def remove_result_pressing(vl,update):
	result = vl.result
	crafting["results"].remove(result)
	update(crafting.get("results"),True)
	print(crafting)

def add_result_pressing(update):
	result = {"item": "","count": 1, "chance": 100}
	crafting["results"].append(result)
	print(crafting)
	update(crafting.get("results"),True)

def update_json_text_box(text):
	try:
		crafting["json"] = json.loads(text)
	except:
		pass
	print(crafting)

def update_vortex(text):
	crafting["vortex"] = str(text)


def update_crafting_key(key,val):
	crafting[key] = val
	print(crafting)



def update_pressing_slot_images(buttons):
		for i in list(range(0,len(crafting.get("results")))):
			if not buttons[i].result.get("item") == "":
				item = remove_mod(buttons[i].result.get("item"))
				tag = False
				if str(buttons[i].result.get("item")).startswith("tag:"):
					tag = True
				if settings.config.get("BorderRender") == True:
					image = border_render.generate_border(db_engine.search_path(item,tag=tag))
				else:
					image = ImageTk.PhotoImage(Image.open(db_engine.search_path(item,tag=tag)).resize((54,54),resample=0))
			else:
				if settings.config.get("BorderRender") == True:
					image = border_render.generate_border("./assets/textures/slot00.png")
				else:
					image = ImageTk.PhotoImage(Image.open("./assets/textures/slot00.png").resize((54,54),resample=0))
			buttons[i].config(image=image)
			buttons[i].image=image


def set_result_pressing(callback):
	item = get_selected_item()
	if not item == None:
		result = callback.result
		count = result.get("count")
		chance = result.get("chance")
		try:
			crafting["results"].remove(result)
		except:
			pass
		result = {"item": item,"count": count,"chance": chance}
		callback.result = result
		crafting["results"].append(result)
		tag = False
		if str(item).startswith("tag:"):
			tag = True
		if settings.config.get("BorderRender") == True:
			image = border_render.generate_border(db_engine.search_path(remove_mod(item),tag=tag))
		else:
			image = ImageTk.PhotoImage(Image.open(db_engine.search_path(remove_mod(item),tag=tag)).resize((54,54),resample=0))
		callback.config(image=image)
		callback.image=image
	
	print(crafting)


class filter_screen(ctk.CTkFrame):
	def __init__(self, master, width = 200, height = 200,update_func = None,palet = None):
		super().__init__(master, width, height)
		self.update_func = update_func
		self.palet = palet
		self.setup()
		self.create()
		self.set_default_val
	def setup(self):
		self.block_checkbox1_value = tk.IntVar(inv_screen)
		self.block_checkbox2_value = tk.IntVar(inv_screen)
		self.block_checkbox3_value = tk.IntVar(inv_screen)
		self.block_checkbox4_value = tk.IntVar(inv_screen)


	def create(self):
		ctk.CTkLabel(self,text="Inventory Filter").pack(side="top",pady=2,padx=2,fill="x")
		self.block_checkbox1 = ctk.CTkCheckBox(self,text="blocks",variable=self.block_checkbox1_value,onvalue=1,offvalue=0,command=lambda: self.update_func(self.block_checkbox1_value,self.block_checkbox2_value,self.block_checkbox3_value,self.block_checkbox4_value,self.palet)).pack(side="top",pady=2,padx=2,fill="x")
		self.block_checkbox2 = ctk.CTkCheckBox(self,text="items",variable=self.block_checkbox2_value,onvalue=1,offvalue=0,command=lambda: self.update_func(self.block_checkbox1_value,self.block_checkbox2_value,self.block_checkbox3_value,self.block_checkbox4_value,self.palet)).pack(side="top",pady=2,padx=2,fill="x")
		self.block_checkbox3 = ctk.CTkCheckBox(self,text="fluids",variable=self.block_checkbox3_value,onvalue=1,offvalue=0,command=lambda: self.update_func(self.block_checkbox1_value,self.block_checkbox2_value,self.block_checkbox3_value,self.block_checkbox4_value,self.palet)).pack(side="top",pady=2,padx=2,fill="x")
		self.block_checkbox4 = ctk.CTkCheckBox(self,text="tags",variable=self.block_checkbox4_value,onvalue=1,offvalue=0,command=lambda: self.update_func(self.block_checkbox1_value,self.block_checkbox2_value,self.block_checkbox3_value,self.block_checkbox4_value,self.palet)).pack(side="top",pady=2,padx=2,fill="x")
	
	def set_default_val(self):
		self.block_checkbox1_value.set(1)
		self.block_checkbox2_value.set(1)
		self.block_checkbox3_value.set(1)
		self.block_checkbox4_value.set(1)


def update_saved_palet_database_cl():
	try:
		if not saved_palet_database.curselection():
			saved_palet_database = db_engine.loaddatabase()
			update_palet(saved_palet,saved_palet_database)
	except:
		pass

def set_c(data):
	global crafting
	crafting = data

def cc(v):
	global latest_item
	latest_item = None

def inv_open(root):
	global search_entry_saved,search_entry
	global palet,saved_palet
	global database
	global preview_item
	global inv_screen
	global saved_palet_database
	global I_slot00,latest_item

	if inv_screen is None:
		inv_screen=ctk.CTkFrame(root,height=600,width=700)
		inv_screen.place(y=1,x=1020)
		
		saved_palet_database = db_engine.loaddatabase()
		I_slot00=ImageTk.PhotoImage(Image.open("assets/textures/slot00.png").resize((54,54),resample=0))
		inv_screen.bind("<Button-1>",cc)
		def lose_focus(event):
			global latest_item
			if not isinstance(event.widget,(tk.Entry, tk.Listbox)):
				inv_screen.focus_set()
				palet.selection_clear(0, tk.END)
				latest_item = None
				saved_palet.selection_clear(0, tk.END)
				none_image = CTkImage(light_image=Image.open("./assets/textures/none.png"), size=(180, 180))
				preview_item.configure(image=none_image)
				preview_item.image = none_image
		inv_screen.bind("<Button-1>",lose_focus, add="+")		

		palet = tk.Listbox(inv_screen,height=28,width=37,background=light_bg_color,foreground=text_color,highlightbackground=outline_collor,highlightcolor=outline_collor,selectbackground=outline_collor)
		palet.place(x=360,y=28)
		database = db_engine.getall()
		update_palet(palet,database)
		search_entry = ctk.CTkEntry(inv_screen,height=21,width=298)
		search_entry.place(x=358,y=2)
		shortcut(search_entry)

		search_entry.bind("<KeyRelease>", lambda event:update_palet(palet,search(str(search_entry.get()),database)))
		saved_palet = tk.Listbox(inv_screen,height=18,width=38,background=light_bg_color,foreground=text_color,highlightbackground=outline_collor,highlightcolor=outline_collor,selectbackground=outline_collor)
		saved_palet.place(x=10,y=28)
		preview_item = ctk.CTkLabel(inv_screen,text=None,height=54,width=54)
		preview_item.place(x=10,y=405)
		Image_none = CTkImage(light_image=Image.open("./assets/textures/none.png"), size=(180, 180))
		preview_item.configure(image=Image_none)
		saved_palet.bind("<<ListboxSelect>>", lambda event:load_item(saved_palet))
		palet.bind("<<ListboxSelect>>",lambda event:load_item(palet))

		saved_palet.bind("<Button-3>", lambda event:remove_item(saved_palet))
		palet.bind("<Button-3>",lambda event:add_item(palet,saved_palet))
		
		update_palet(saved_palet,saved_palet_database)
		search_entry_saved = ctk.CTkEntry(inv_screen,height=21,width=306)
		search_entry_saved.place(x=8,y=2)
		search_entry_saved.bind("<KeyRelease>", lambda event:update_palet(saved_palet,search(str(search_entry_saved.get()),database=db_engine.loaddatabase(db_engine.saved_database_name))))
		shortcut(search_entry_saved)
		#-------------
		filter_screen_frame = filter_screen(inv_screen,width=120,height=180,update_func=update_filter,palet=palet)
		#filter_screen_frame.place(x=215,y=423)



		








