import core.ui.easydialog as easydialog
import tkinter as tk
from tkinter import ttk
from PIL import Image,ImageTk
import core.services as services
from core import centerlib
import core.db_engine as db_engine
from tkinter import ttk
import importlib
import requests
import core.ui.settings as settings
import os
from tkinter import font
from PIL import ImageFont
import re
from core.ui import colorschem
from core import DataAPI
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
import tkcode
import sys
import customtkinter as ctk
import threading
import subprocess
import easygui
import time
import json
from core import waste_of_time
import datetime
from core.tknodesystem import *
import uuid

text_color = colorschem.text_color
ctk.set_appearance_mode(settings.config.get("mode"))
ctk.set_default_color_theme(os.path.join("./assets/themes",f"{settings.config.get("them")}.json"))

def set_color():
	ctk.set_default_color_theme(os.path.join("./assets/themes",f"{settings.config.get("them")}.json"))
def set_mode():
	ctk.set_appearance_mode(settings.config.get("mode"))
DataAPI.set_updating_vars(set_mode,set_color)
socket_radius=10

outline_collor = colorschem.outline_collor
dark_bg_color = colorschem.dark_bg_color
light_bg_color = colorschem.light_bg_color

settings_screen = None
element_database = []
running = True
def root_stop():
	global running
	c = easygui.ynbox("Are You Sure?")
	if c:
		running = False
		root.destroy()
		root.quit()
		exit(0)


def tolouncher():
	global running
	try:
		subprocess.Popen([sys.executable, "main.py"])
		print("starting...")
	except Exception as e:
		print(f"Error running main.py: {e}")
	finally:
		running = False
		root.destroy()
		root.quit()
		exit(0)

def auto_close(event):
    """Automaticky uzavírá závorky a uvozovky v CTkTextbox."""
    textbox = event.widget
    text = event.char
    
    pairs = {"(": ")", "[": "]", "{": "}", "\"": "\"", "'": "'"}
    
    if text in pairs:
        textbox.insert("insert", pairs[text])
        textbox.mark_set("insert", "insert-1c")

auto_indent_correct = True
auto_indent_correct_m = ""
def json_auto_indent_correct(textbox,run=False):
	global auto_indent_correct,auto_indent_correct_m
	if auto_indent_correct or run:
		try:
			if not str(textbox.get(0.0,ctk.END)) == auto_indent_correct_m:
				auto_indent_correct_m = str(textbox.get(0.0,ctk.END))
				data = json.loads(textbox.get(0.0,ctk.END))
				cursor_pos = textbox.index("insert") 
				textbox.delete(0.0,ctk.END)
				textbox.insert(0.0,json.dumps(data,indent="\t"))
				textbox.mark_set("insert", cursor_pos)
		except:
			pass

class TextBoxCommander:
	def __init__(self, textbox: ctk.CTkTextbox):
		self.textbox = textbox
		self.textbox.bind("<Control-f>", self.open_search)
		self.textbox.bind("<KeyRelease>", lambda e: self.apply_highlights())
		self.keywords = {}
		
	def open_search(self, event=None):
		search_window = ctk.CTkToplevel()
		search_window.title("Find")
		search_window.geometry("250x100")
		
		ctk.CTkLabel(search_window, text="Find:").pack(pady=5)
		search_entry = ctk.CTkEntry(search_window)
		search_entry.pack(pady=5)
		
		def update_highlight(event=None):
			self.highlight_search(search_entry.get(), "#FFFF00")
		
		search_entry.bind("<KeyRelease>", update_highlight)
		search_entry.bind("<Return>", lambda e: search_window.destroy())
		search_entry.bind("<Escape>", lambda e: search_window.destroy())
		services.shortcut(search_entry)
		search_entry.focus_set()
		
	def highlight_search(self, keyword, color):
		self.textbox.tag_remove("search", "1.0", ctk.END)
		if not keyword:
			return
		
		start = "1.0"
		while True:
			start = self.textbox.search(keyword, start, stopindex=ctk.END, nocase=True)
			if not start:
				break
			end = f"{start}+{len(keyword)}c"
			self.textbox.tag_add("search", start, end)
			self.textbox.tag_config("search", background=color)
			start = end
		
	def add_mark_keywords(self, color: str, words: list):
		self.keywords[color] = words
		self.apply_highlights()
		
	def apply_highlights(self, event=None):
		for tag in self.textbox.tag_names():
			if not str(tag) == "json_error":
				self.textbox.tag_remove(tag, "1.0", ctk.END)
		
		for color, words in self.keywords.items():
			for word in words:
				start = "1.0"
				while True:
					start = self.textbox.search(word, start, stopindex=ctk.END, nocase=True)
					if not start:
						break
					end = f"{start}+{len(word)}c"
					self.textbox.tag_add(word, start, end)
					self.textbox.tag_config(word, foreground=color)
					start = end


def get_widget_by_name(widget_name):
	"""Vrátí objekt widgetu podle jeho názvu."""
	return globals().get(widget_name, None)

def load_custom_font(ttf_file, font_size):
	pil_font = ImageFont.truetype(ttf_file, font_size)
	font_tuple = (pil_font.getname()[0], font_size)
	return font.Font(family=font_tuple[0], size=font_tuple[1])

files = os.listdir("./")
if not db_engine.database_path.replace("./","") in files:
	easydialog.msgbox("Database is not connected\nplease connect database")
	root_stop()


aditional_types = []
def add_aditional(additionals=[]):
	global aditional_types
	aditional_types += additionals

DataAPI.set_add_aditional_types_func(add_aditional)

root_window = ctk.CTk()
root_window.title("Craftix Studio 2025")
root_window.geometry("1730x850")
services.inv_open(root_window)


def apply_dark_theme_to_notebook(notebook: ttk.Notebook):
	style = ttk.Style()
	style.theme_use("clam")
	style.configure("TNotebook", background="#333333", borderwidth=0, relief="flat")
	style.configure("TNotebook.Tab", background="#444444", foreground="white", padding=[10, 5], borderwidth=0)
	style.map("TNotebook.Tab", background=[("selected", "#222222")])


tab_menu = ttk.Notebook(root_window,width=999,height=571)
tab_menu.place(x=10,y=4)
apply_dark_theme_to_notebook(tab_menu)
root = ctk.CTkFrame(tab_menu,width=1000,height=600)
root.place(y=1,x=10)

DataAPI.set_gca(root)

settings_frame=ctk.CTkFrame(tab_menu,height=571,width=999)
settings_frame.place(x=10,y=1)

remove_frame=ctk.CTkFrame(tab_menu,height=571,width=999)
remove_frame.place(x=10,y=1)

remove_textbox=ctk.CTkTextbox(remove_frame,height=571,width=999)
remove_textbox.pack(side="bottom",fill="both")


caption_labels = []
class caption(ctk.CTkLabel):
	global caption_labels
	def __init__(self, master, width = 0, height = 28, corner_radius = None, bg_color = "transparent", fg_color = None, text_color = None, text_color_disabled = None, text = "CTkLabel", font = None, image = None, compound = "center", anchor = "center", wraplength = 0, **kwargs):
		super().__init__(master, width, height, corner_radius, bg_color, fg_color, text_color, text_color_disabled, text, font, image, compound, anchor, wraplength, **kwargs)
		caption_labels.append(self)


def final_remove_ids(value):
	db_engine.save_removed_crfating_ids(ids=value)

def check_json_syntax(event=None):
    """Zkontroluje syntaxi JSONu a zvýrazní chybnou řádku červeně."""
    content = tags_edit_textbox.get("1.0", "end-1c")
    try:
        json.loads(content)
        tags_edit_textbox.tag_remove("json_error", "1.0", "end")
    except json.JSONDecodeError as e:
        line, column = e.lineno, e.colno

        start_index = f"{line}.0"
        end_index = f"{line}.end"
        tags_edit_textbox.tag_add("json_error", start_index, end_index)
        tags_edit_textbox.tag_config("json_error", background="red", foreground="white")


tags_frame=ctk.CTkFrame(tab_menu,height=571,width=999)
tags_frame.place(x=10,y=1)

tags_textbox=ctk.CTkTextbox(tags_frame,height=571,width=999)
tags_textbox.pack(side="bottom",fill="both")


class DragMode:
	def __init__(self, widget):
		self.widget = widget
		widget.bind("<Button-1>", self.drag_start)
		widget.bind("<B1-Motion>", self.drag_move)
	def drag_start(self, event):
		self.widget.startX = event.x
		self.widget.startY = event.y
	def drag_move(self, event):
		x = self.widget.winfo_x() - self.widget.startX + event.x
		y = self.widget.winfo_y() - self.widget.startY + event.y
		self.widget.place(x=x, y=y)


tags_edit_frame=ctk.CTkFrame(tab_menu,height=571,width=999)
tags_edit_frame.place(x=10,y=1)

tags_edit_textbox=ctk.CTkTextbox(tags_edit_frame,height=571,width=999)
tags_edit_textbox.pack(side="bottom",fill="both")


def update_custum_parms(commander,data,color="#F8E45C"):
	try:
		data = json.loads(data)
		keys = data.keys()
		k = []
		for key in keys:
			k.append(f"\"{key}\":")
		commander.add_mark_keywords(color,k)

	except:
		pass

tags_edit_textbox.insert(0.0,json.dumps(db_engine.load_tags_edits(),indent="\t"))
tags_edit_textbox.bind("<KeyPress>",auto_close)
tags_edit_textbox.bind("<KeyRelease>",check_json_syntax)
tags_edit_textbox.configure(tabs=("4m",))
tags_edit_textbox.bind("<KeyRelease>",lambda v: json_auto_indent_correct(tags_edit_textbox))

tags_editor_commander = TextBoxCommander(tags_edit_textbox)
tags_editor_commander.add_mark_keywords("#C061CB",["{","}"])
tags_editor_commander.add_mark_keywords("##F8E45C",["(",")"])
tags_editor_commander.add_mark_keywords("#3584E4",["[","]"])
tags_editor_commander.add_mark_keywords("#ED333B",["\"","\"","'","'"])
tags_editor_commander.add_mark_keywords("#00ff00",["\"add\"","\"rm\"","\"remove\"","'add'","'rm'","'remove'"])
tags_editor_commander.add_mark_keywords("#8FF0A4",["0","1","2","3","4","5","6","7","8","9"])
update_custum_parms(tags_editor_commander,tags_edit_textbox.get(0.0,ctk.END))
tags_edit_textbox.bind("<KeyRelease>",lambda v: update_custum_parms(tags_editor_commander,tags_edit_textbox.get(0.0,ctk.END)))


def save_tags_edits():
	try:
		db_engine.save_tags_edits(json.loads(tags_edit_textbox.get(1.0,ctk.END)))
	except:
		print("[error] error in saving tags edits")

def update_tag_database():
	tags = []
	value = tags_textbox.get("1.0",tk.END)
	value = value.replace("\n","")
	value = value.split(";")
	for i  in value:
		if not i == "":
			tags.append(i)
	db_engine.update_tags(tags=tags)
	database = db_engine.getall()
	
	services.update_main_palet(database)

def update_database():
	database = db_engine.getall()
	services.update_palet(services.palet,database)

hide_c_frame=ctk.CTkFrame(tab_menu,height=571,width=999)
hide_c_frame.place(x=10,y=1)

hide_c_textbox=ctk.CTkTextbox(hide_c_frame,height=571,width=999)
hide_c_textbox.pack(side="bottom",fill="both")



def load_array_textbox(box, data):
	try:
		cursor_pos = box.index("insert") 
	except:
		pass
	box.delete("0.1", tk.END)
	for i, item in enumerate(data):
		if i < len(data) - 1:
			item = item.replace(".png","")
			box.insert(tk.END, f"{str(item)};\n")
		else:
			item = item.replace(".png","")
			box.insert(tk.END, f"{str(item)}\n")
	try:
		box.mark_set("insert", cursor_pos)
	except:
		pass
load_array_textbox(tags_textbox,db_engine.load_tags())
load_array_textbox(remove_textbox,db_engine.load_removed_crfating_ids())
load_array_textbox(hide_c_textbox,db_engine.load_hidden_crfating_ids())
def update_removed_ids():
	inp = remove_textbox.get("1.0",ctk.END)
	inp = inp.replace("\n","")
	final_remove_ids(inp.split(";"))

def update_hide_c():
	inp = hide_c_textbox.get("0.1",ctk.END)
	inp = inp.replace("\n","")
	db_engine.save_hidden_crfating_ids(ids=inp.split(";"))

remove_text_box_commander = TextBoxCommander(remove_textbox)
remove_text_box_commander.add_mark_keywords("#00ffbb",[";"])
remove_text_box_commander.add_mark_keywords("#aa00cc",[":","/"])
remove_text_box_commander.add_mark_keywords("#ff0000",["*",",","=",'"',"'","."])

tags_text_box_commander = TextBoxCommander(tags_textbox)
tags_text_box_commander.add_mark_keywords("#00ffbb",[";"])
tags_text_box_commander.add_mark_keywords("#aa00cc",[":","/"])
tags_text_box_commander.add_mark_keywords("#ff0000",["*",",","=",'"',"'",".png","."])

hide_c_text_box_commander = TextBoxCommander(hide_c_textbox)
hide_c_text_box_commander.add_mark_keywords("#00ffbb",[";"])
hide_c_text_box_commander.add_mark_keywords("#aa00cc",[":","/"])
hide_c_text_box_commander.add_mark_keywords("#ff0000",["*",",","=",'"',"'","."])


tab_menu.add(root,text="Editor")
tab_menu.add(remove_frame,text="Removed Craftings")
tab_menu.add(tags_frame,text="Tags")
tab_menu.add(tags_edit_frame,text="Tags Editor")
tab_menu.add(hide_c_frame,text="Hidden Craftings")
tab_menu.add(settings_frame,text="Settings")
settings.open(settings_frame)


root_window.protocol("WM_DELETE_WINDOW",lambda: root_stop())

underlined_font0 = font.Font(family="Helvetica", size=12, underline=True)

#ico = Image.open('./textures/icon.ico')
#photo = ImageTk.PhotoImage(ico)
#root_window.wm_iconphoto(False, photo)

DataAPI.set_root(root_window)
DataAPI.set_get_global_func(get_widget_by_name)

I_arrow00=ImageTk.PhotoImage(Image.open("./assets/textures/arrow00.png"))
I_slot00=ImageTk.PhotoImage(Image.open("./assets/textures/slot00.png").resize((54,54),resample=0))
def redirect_console_to_textbox(text_widget, log_file_path, highlight_green=None, highlight_red=None, highlight_yellow=None):
    if highlight_green is None:
        highlight_green = ["[ok]:", "initialized", "success", "running", "accepted", "[Success] all systems go"]
    if highlight_red is None:
        highlight_red = ["error", "denied", "[Error]", "[ERROR]"]
    if highlight_yellow is None:
        highlight_yellow = ["info", "[info]"]

    # Ověření, že složka logs existuje
    os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

    def write_to_textbox(message):
        text_widget.configure(state='normal')

        # Přidání textu do textového widgetu
        start_index = text_widget.index('end-1c')
        text_widget.insert('end', message + "\n")
        end_index = text_widget.index('end-1c')

        # Zvýraznění klíčových slov
        for word in highlight_green:
            highlight_word(text_widget, word, start_index, end_index, "#00ff00")

        for word in highlight_red:
            highlight_word(text_widget, word, start_index, end_index, "#ff0000")

        for word in highlight_yellow:
            highlight_word(text_widget, word, start_index, end_index, "#ffff00")

        text_widget.see('end')  # Automatické scrollování na konec
        text_widget.configure(state='disabled')

        # Zápis do souboru s časovým razítkem
        with open(log_file_path, "a", encoding="utf-8") as log_file:
            timestamp = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S] ")
            log_file.write(timestamp + message + "\n")

    def highlight_word(widget, word, start, end, color):
        start_pos = widget.search(word, start, stopindex=end, nocase=True)
        while start_pos:
            end_pos = f"{start_pos}+{len(word)}c"
            widget.tag_add(color, start_pos, end_pos)
            widget.tag_config(color, foreground=color)
            start_pos = widget.search(word, end_pos, stopindex=end, nocase=True)

    class ConsoleStream:
        def write(self, message):
            if message.strip():
                text_widget.after(0, write_to_textbox, message)

        def flush(self):
            pass

    return ConsoleStream()

def create_debug_window(root=None, text_box_height=240, text_box_width=322, bg_color="black", fg_color="white"):
    # Logovací soubor
    log_file_path = "logs/app.log"

    # Vytvoření Text widgetu
    text_box = ctk.CTkTextbox(root, wrap='word', height=text_box_height, width=text_box_width)
    text_box.pack(fill='both', expand=True)
    text_box.configure(state='disabled')

    # Přesměrování konzolového výstupu + logování
    sys.stdout = redirect_console_to_textbox(text_box, log_file_path)
    sys.stderr = redirect_console_to_textbox(text_box, log_file_path)

    # Vytvoření vlákna pro ukázkový výstup
    def generate_debug_output():
        print("Debug Window initialized!")

    threading.Thread(target=generate_debug_output, daemon=True).start()

# Použití v aplikaci
debug_frame = ctk.CTkFrame(root_window)
debug_frame.place(x=1394, y=603)

create_debug_window(debug_frame, fg_color="white", bg_color="black")
#waste_of_time.start_printing()



def valide_input(value):
	return value.isdigit() or value==""
vcmd=root.register(valide_input)

def lose_focus(event):
	if isinstance(event.widget,tk.Entry):
		return
	root.focus_set()
root.bind("<Button-1>",lose_focus)

def on_click(event):
	if event.num == 1:
		print("Levé tlačítko")
	elif event.num == 2:
		print("Středové tlačítko")
	elif event.num == 3:
		print("Pravé tlačítko")
	else:
		print("Neznámé tlačítko")
	#module01_slot01.bind("<Button-1>",on_click)
	#module01_slot01.bind("<Button-2>",on_click)
	#module01_slot01.bind("<Button-3>",on_click)

modules = ""

def add_into_element_database(element):
	global element_database
	element_database.append(element)

DataAPI.set_aitelf(add_into_element_database)

playgrounds = {}

def update_workspace(results = []):
	global modules, element_database, caption_labels, playgrounds
	
	for element in element_database:
		try:
			element.destroy()
			element.master.update()
		except:
			pass
	
	for element in caption_labels:
		try:
			element.destroy()
		except:
			pass
	
	if modules == "mechanical_crafting":#mechanical_crafting

		offset:int=54

		module06_slot00=tk.Button(root,highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module06_slot00,1))
		module06_slot00.place(x=280,y=60)

		module06_slot01=tk.Button(root,highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module06_slot01,2))
		module06_slot01.place(x=int(module06_slot00.place_info()["x"])+offset,y=int(module06_slot00.place_info()["y"]))

		module06_slot02=tk.Button(root,highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module06_slot02,3))
		module06_slot02.place(x=int(module06_slot01.place_info()["x"])+offset,y=int(module06_slot01.place_info()["y"]))

		module06_slot03=tk.Button(root,highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module06_slot03,4))
		module06_slot03.place(x=int(module06_slot02.place_info()["x"])+offset,y=int(module06_slot02.place_info()["y"]))

		module06_slot04=tk.Button(root,highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module06_slot04,5))
		module06_slot04.place(x=int(module06_slot03.place_info()["x"])+offset,y=int(module06_slot03.place_info()["y"]))

		module06_slot05=tk.Button(root,highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module06_slot05,6))
		module06_slot05.place(x=int(module06_slot04.place_info()["x"])+offset,y=int(module06_slot04.place_info()["y"]))

		module06_slot06=tk.Button(root,highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module06_slot06,7))
		module06_slot06.place(x=int(module06_slot05.place_info()["x"])+offset,y=int(module06_slot05.place_info()["y"]))
		
		module06_slot07=tk.Button(root,highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module06_slot07,8))
		module06_slot07.place(x=int(module06_slot06.place_info()["x"])+offset,y=int(module06_slot06.place_info()["y"]))

		module06_slot08=tk.Button(root,highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module06_slot08,9))
		module06_slot08.place(x=int(module06_slot07.place_info()["x"])+offset,y=int(module06_slot07.place_info()["y"]))



		module06_slot09=tk.Button(root,highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module06_slot09,10))
		module06_slot09.place(x=280,y=int(module06_slot00.place_info()["y"])+offset)

		module06_slot10=tk.Button(root,highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module06_slot10,11))
		module06_slot10.place(x=int(module06_slot09.place_info()["x"])+offset,y=int(module06_slot01.place_info()["y"])+offset)

		module06_slot11=tk.Button(root,highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module06_slot11,12))
		module06_slot11.place(x=int(module06_slot10.place_info()["x"])+offset,y=int(module06_slot02.place_info()["y"])+offset)

		module06_slot12=tk.Button(root,highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module06_slot12,13))
		module06_slot12.place(x=int(module06_slot11.place_info()["x"])+offset,y=int(module06_slot03.place_info()["y"])+offset)

		module06_slot13=tk.Button(root,highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module06_slot13,14))
		module06_slot13.place(x=int(module06_slot12.place_info()["x"])+offset,y=int(module06_slot04.place_info()["y"])+offset)

		module06_slot14=tk.Button(root,highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module06_slot14,15))
		module06_slot14.place(x=int(module06_slot13.place_info()["x"])+offset,y=int(module06_slot05.place_info()["y"])+offset)
		
		module06_slot15=tk.Button(root,highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module06_slot15,16))
		module06_slot15.place(x=int(module06_slot14.place_info()["x"])+offset,y=int(module06_slot06.place_info()["y"])+offset)

		module06_slot16=tk.Button(root,highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module06_slot16,17))
		module06_slot16.place(x=int(module06_slot15.place_info()["x"])+offset,y=int(module06_slot07.place_info()["y"])+offset)

		module06_slot17=tk.Button(root,highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module06_slot17,18))
		module06_slot17.place(x=int(module06_slot16.place_info()["x"])+offset,y=int(module06_slot08.place_info()["y"])+offset)


		module06_slot18=tk.Button(root,highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module06_slot18,19))
		module06_slot18.place(x=280,y=int(module06_slot09.place_info()["y"])+offset)

		module06_slot19=tk.Button(root,highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module06_slot19,20))
		module06_slot19.place(x=int(module06_slot09.place_info()["x"])+offset,y=int(module06_slot10.place_info()["y"])+offset)

		module06_slot20=tk.Button(root,highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module06_slot20,21))
		module06_slot20.place(x=int(module06_slot10.place_info()["x"])+offset,y=int(module06_slot11.place_info()["y"])+offset)

		module06_slot21=tk.Button(root,highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module06_slot21,22))
		module06_slot21.place(x=int(module06_slot11.place_info()["x"])+offset,y=int(module06_slot12.place_info()["y"])+offset)

		module06_slot22=tk.Button(root,highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module06_slot22,23))
		module06_slot22.place(x=int(module06_slot12.place_info()["x"])+offset,y=int(module06_slot13.place_info()["y"])+offset)

		module06_slot23=tk.Button(root,highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module06_slot23,24))
		module06_slot23.place(x=int(module06_slot13.place_info()["x"])+offset,y=int(module06_slot14.place_info()["y"])+offset)
		
		module06_slot24=tk.Button(root,highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module06_slot24,25))
		module06_slot24.place(x=int(module06_slot14.place_info()["x"])+offset,y=int(module06_slot15.place_info()["y"])+offset)

		module06_slot25=tk.Button(root,highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module06_slot25,26))
		module06_slot25.place(x=int(module06_slot15.place_info()["x"])+offset,y=int(module06_slot16.place_info()["y"])+offset)

		module06_slot26=tk.Button(root,highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module06_slot26,27))
		module06_slot26.place(x=int(module06_slot16.place_info()["x"])+offset,y=int(module06_slot17.place_info()["y"])+offset)


		module06_slot27=tk.Button(root,highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module06_slot27,28))
		module06_slot27.place(x=280,y=int(module06_slot18.place_info()["y"])+offset)

		module06_slot28=tk.Button(root,highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module06_slot28,29))
		module06_slot28.place(x=int(module06_slot09.place_info()["x"])+offset,y=int(module06_slot19.place_info()["y"])+offset)

		module06_slot29=tk.Button(root,highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module06_slot29,30))
		module06_slot29.place(x=int(module06_slot10.place_info()["x"])+offset,y=int(module06_slot20.place_info()["y"])+offset)

		module06_slot30=tk.Button(root,highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module06_slot30,31))
		module06_slot30.place(x=int(module06_slot11.place_info()["x"])+offset,y=int(module06_slot21.place_info()["y"])+offset)

		module06_slot31=tk.Button(root,highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module06_slot31,32))
		module06_slot31.place(x=int(module06_slot12.place_info()["x"])+offset,y=int(module06_slot22.place_info()["y"])+offset)

		module06_slot32=tk.Button(root,highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module06_slot32,33))
		module06_slot32.place(x=int(module06_slot13.place_info()["x"])+offset,y=int(module06_slot23.place_info()["y"])+offset)
		
		module06_slot33=tk.Button(root,highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module06_slot33,34))
		module06_slot33.place(x=int(module06_slot14.place_info()["x"])+offset,y=int(module06_slot24.place_info()["y"])+offset)

		module06_slot34=tk.Button(root,highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module06_slot34,35))
		module06_slot34.place(x=int(module06_slot15.place_info()["x"])+offset,y=int(module06_slot25.place_info()["y"])+offset)

		module06_slot35=tk.Button(root,highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module06_slot35,36))
		module06_slot35.place(x=int(module06_slot16.place_info()["x"])+offset,y=int(module06_slot26.place_info()["y"])+offset)


		module06_slot36=tk.Button(root,highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module06_slot36,37))
		module06_slot36.place(x=280,y=int(module06_slot27.place_info()["y"])+offset)

		module06_slot37=tk.Button(root,highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module06_slot37,38))
		module06_slot37.place(x=int(module06_slot09.place_info()["x"])+offset,y=int(module06_slot28.place_info()["y"])+offset)

		module06_slot38=tk.Button(root,highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module06_slot38,39))
		module06_slot38.place(x=int(module06_slot10.place_info()["x"])+offset,y=int(module06_slot29.place_info()["y"])+offset)

		module06_slot39=tk.Button(root,highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module06_slot39,40))
		module06_slot39.place(x=int(module06_slot11.place_info()["x"])+offset,y=int(module06_slot30.place_info()["y"])+offset)

		module06_slot40=tk.Button(root,highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module06_slot40,41))
		module06_slot40.place(x=int(module06_slot12.place_info()["x"])+offset,y=int(module06_slot31.place_info()["y"])+offset)

		module06_slot41=tk.Button(root,highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module06_slot41,42))
		module06_slot41.place(x=int(module06_slot13.place_info()["x"])+offset,y=int(module06_slot32.place_info()["y"])+offset)
		
		module06_slot42=tk.Button(root,highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module06_slot42,43))
		module06_slot42.place(x=int(module06_slot14.place_info()["x"])+offset,y=int(module06_slot33.place_info()["y"])+offset)

		module06_slot43=tk.Button(root,highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module06_slot43,44))
		module06_slot43.place(x=int(module06_slot15.place_info()["x"])+offset,y=int(module06_slot34.place_info()["y"])+offset)

		module06_slot44=tk.Button(root,highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module06_slot44,45))
		module06_slot44.place(x=int(module06_slot16.place_info()["x"])+offset,y=int(module06_slot35.place_info()["y"])+offset)


		module06_slot45=tk.Button(root,highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module06_slot45,46))
		module06_slot45.place(x=280,y=int(module06_slot36.place_info()["y"])+offset)

		module06_slot46=tk.Button(root,highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module06_slot46,47))
		module06_slot46.place(x=int(module06_slot09.place_info()["x"])+offset,y=int(module06_slot37.place_info()["y"])+offset)

		module06_slot47=tk.Button(root,highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module06_slot47,48))
		module06_slot47.place(x=int(module06_slot10.place_info()["x"])+offset,y=int(module06_slot38.place_info()["y"])+offset)

		module06_slot48=tk.Button(root,highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module06_slot48,49))
		module06_slot48.place(x=int(module06_slot11.place_info()["x"])+offset,y=int(module06_slot39.place_info()["y"])+offset)

		module06_slot49=tk.Button(root,highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module06_slot49,50))
		module06_slot49.place(x=int(module06_slot12.place_info()["x"])+offset,y=int(module06_slot40.place_info()["y"])+offset)

		module06_slot50=tk.Button(root,highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module06_slot50,51))
		module06_slot50.place(x=int(module06_slot13.place_info()["x"])+offset,y=int(module06_slot41.place_info()["y"])+offset)
		
		module06_slot51=tk.Button(root,highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module06_slot51,52))
		module06_slot51.place(x=int(module06_slot14.place_info()["x"])+offset,y=int(module06_slot42.place_info()["y"])+offset)

		module06_slot52=tk.Button(root,highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module06_slot52,53))
		module06_slot52.place(x=int(module06_slot15.place_info()["x"])+offset,y=int(module06_slot43.place_info()["y"])+offset)

		module06_slot53=tk.Button(root,highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module06_slot53,54))
		module06_slot53.place(x=int(module06_slot16.place_info()["x"])+offset,y=int(module06_slot44.place_info()["y"])+offset)


		module06_slot54=tk.Button(root,highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module06_slot54,55))
		module06_slot54.place(x=280,y=int(module06_slot45.place_info()["y"])+offset)

		module06_slot55=tk.Button(root,highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module06_slot55,56))
		module06_slot55.place(x=int(module06_slot09.place_info()["x"])+offset,y=int(module06_slot46.place_info()["y"])+offset)

		module06_slot56=tk.Button(root,highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module06_slot56,57))
		module06_slot56.place(x=int(module06_slot10.place_info()["x"])+offset,y=int(module06_slot47.place_info()["y"])+offset)

		module06_slot57=tk.Button(root,highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module06_slot57,58))
		module06_slot57.place(x=int(module06_slot11.place_info()["x"])+offset,y=int(module06_slot48.place_info()["y"])+offset)

		module06_slot58=tk.Button(root,highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module06_slot58,59))
		module06_slot58.place(x=int(module06_slot12.place_info()["x"])+offset,y=int(module06_slot49.place_info()["y"])+offset)

		module06_slot59=tk.Button(root,highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module06_slot59,60))
		module06_slot59.place(x=int(module06_slot13.place_info()["x"])+offset,y=int(module06_slot50.place_info()["y"])+offset)
		
		module06_slot60=tk.Button(root,highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module06_slot60,61))
		module06_slot60.place(x=int(module06_slot14.place_info()["x"])+offset,y=int(module06_slot51.place_info()["y"])+offset)

		module06_slot61=tk.Button(root,highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module06_slot61,62))
		module06_slot61.place(x=int(module06_slot15.place_info()["x"])+offset,y=int(module06_slot52.place_info()["y"])+offset)

		module06_slot62=tk.Button(root,highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module06_slot62,63))
		module06_slot62.place(x=int(module06_slot16.place_info()["x"])+offset,y=int(module06_slot53.place_info()["y"])+offset)


		module06_slot63=tk.Button(root,highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module06_slot63,64))
		module06_slot63.place(x=280,y=int(module06_slot54.place_info()["y"])+offset)

		module06_slot64=tk.Button(root,highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module06_slot64,65))
		module06_slot64.place(x=int(module06_slot09.place_info()["x"])+offset,y=int(module06_slot55.place_info()["y"])+offset)

		module06_slot65=tk.Button(root,highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module06_slot65,66))
		module06_slot65.place(x=int(module06_slot10.place_info()["x"])+offset,y=int(module06_slot56.place_info()["y"])+offset)

		module06_slot66=tk.Button(root,highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module06_slot66,67))
		module06_slot66.place(x=int(module06_slot11.place_info()["x"])+offset,y=int(module06_slot57.place_info()["y"])+offset)

		module06_slot67=tk.Button(root,highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module06_slot67,68))
		module06_slot67.place(x=int(module06_slot12.place_info()["x"])+offset,y=int(module06_slot58.place_info()["y"])+offset)

		module06_slot68=tk.Button(root,highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module06_slot68,69))
		module06_slot68.place(x=int(module06_slot13.place_info()["x"])+offset,y=int(module06_slot59.place_info()["y"])+offset)
		
		module06_slot69=tk.Button(root,highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module06_slot69,70))
		module06_slot69.place(x=int(module06_slot14.place_info()["x"])+offset,y=int(module06_slot60.place_info()["y"])+offset)

		module06_slot70=tk.Button(root,highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module06_slot70,71))
		module06_slot70.place(x=int(module06_slot15.place_info()["x"])+offset,y=int(module06_slot61.place_info()["y"])+offset)

		module06_slot71=tk.Button(root,highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module06_slot71,72))
		module06_slot71.place(x=int(module06_slot16.place_info()["x"])+offset,y=int(module06_slot62.place_info()["y"])+offset)


		module06_slot72=tk.Button(root,highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module06_slot72,73))
		module06_slot72.place(x=280,y=int(module06_slot63.place_info()["y"])+offset)

		module06_slot73=tk.Button(root,highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module06_slot73,74))
		module06_slot73.place(x=int(module06_slot09.place_info()["x"])+offset,y=int(module06_slot64.place_info()["y"])+offset)

		module06_slot74=tk.Button(root,highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module06_slot74,75))
		module06_slot74.place(x=int(module06_slot10.place_info()["x"])+offset,y=int(module06_slot65.place_info()["y"])+offset)

		module06_slot75=tk.Button(root,highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module06_slot75,76))
		module06_slot75.place(x=int(module06_slot11.place_info()["x"])+offset,y=int(module06_slot66.place_info()["y"])+offset)

		module06_slot76=tk.Button(root,highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module06_slot76,77))
		module06_slot76.place(x=int(module06_slot12.place_info()["x"])+offset,y=int(module06_slot67.place_info()["y"])+offset)

		module06_slot77=tk.Button(root,highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module06_slot77,78))
		module06_slot77.place(x=int(module06_slot13.place_info()["x"])+offset,y=int(module06_slot68.place_info()["y"])+offset)
		
		module06_slot78=tk.Button(root,highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module06_slot78,79))
		module06_slot78.place(x=int(module06_slot14.place_info()["x"])+offset,y=int(module06_slot69.place_info()["y"])+offset)

		module06_slot79=tk.Button(root,highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module06_slot79,80))
		module06_slot79.place(x=int(module06_slot15.place_info()["x"])+offset,y=int(module06_slot70.place_info()["y"])+offset)

		module06_slot80=tk.Button(root,highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module06_slot80,81))
		module06_slot80.place(x=int(module06_slot16.place_info()["x"])+offset,y=int(module06_slot71.place_info()["y"])+offset)	


		module06_slot81=tk.Button(root,borderwidth=0,command=lambda:services.create_crafting(module06_slot81,"result"),highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color,image=I_slot00,highlightthickness=1)
		module06_slot81.place(x=844,y=276)

		module06_arrow00=tk.Button(root,image=I_arrow00,borderwidth=0,highlightthickness=0,background=dark_bg_color,activebackground=light_bg_color)
		module06_arrow00.place(x=772,y=279)

		module06_text00=tk.Entry(root,width=7,validate="key",validatecommand=(vcmd,"%P"),background=light_bg_color,borderwidth=0,highlightthickness=1,highlightbackground=outline_collor,highlightcolor=outline_collor,foreground=text_color)
		module06_text00.place(x=842,y=335)
		module06_text00.bind("<KeyRelease>",lambda event:services.create_crafting_result_count(module06_text00.get()))
		element_database = [module06_slot00,module06_slot01,module06_slot02,module06_slot03,module06_slot04,module06_slot05,module06_slot06,module06_slot07,module06_slot08,module06_slot09,module06_slot10,module06_slot11,module06_slot12,module06_slot13,module06_slot14,module06_slot15,module06_slot16,module06_slot17,module06_slot18,module06_slot19,module06_slot20,module06_slot21,module06_slot22,module06_slot23,module06_slot24,module06_slot25,module06_slot26,module06_slot27,module06_slot28,module06_slot29,module06_slot30,module06_slot31,module06_slot32,module06_slot33,module06_slot34,module06_slot35,module06_slot36,module06_slot37,module06_slot38,module06_slot39,module06_slot40,module06_slot41,module06_slot42,module06_slot43,module06_slot44,module06_slot45,module06_slot46,module06_slot47,module06_slot48,module06_slot49,module06_slot50,module06_slot51,module06_slot52,module06_slot53,module06_slot54,module06_slot55,module06_slot56,module06_slot57,module06_slot58,module06_slot59,module06_slot60,module06_slot61,module06_slot62,module06_slot63,module06_slot64,module06_slot65,module06_slot66,module06_slot67,module06_slot68,module06_slot69,module06_slot70,module06_slot71,module06_slot72,module06_slot73,module06_slot74,module06_slot75,module06_slot76,module06_slot77,module06_slot78,module06_slot79,module06_slot80,module06_slot81,module06_text00,
					  module06_arrow00]


	if modules == "furnace":#furmace

		module01_slot00=tk.Button(root,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module01_slot00,"in"),highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color)
		module01_slot00.place(x=515,y=248)
		module01_slot01=tk.Button(root,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda: services.create_crafting(module01_slot01,"result"),highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color)
		module01_slot01.place(x=642,y=248)
		def update_furnace(event = None):
			services.furnace_parms(cooking_time=str(module01_text00.get()),experience=str(module01_text01.get()),result_count=str(module01_text02.get()))
		module01_frame00 = tk.Frame(root,width=185,height=87,background=light_bg_color)
		module01_frame00.place(x=515,y=152)
		module01_text00=tk.Entry(module01_frame00,width=9,validate="key",validatecommand=(vcmd,"%P"),background=light_bg_color,borderwidth=0,highlightthickness=1,highlightbackground=outline_collor,highlightcolor=outline_collor,foreground=text_color)
		module01_text00.place(x=105,y=33)
		module01_text01=tk.Entry(module01_frame00,width=9,validate="key",validatecommand=(vcmd,"%P"),background=light_bg_color,borderwidth=0,highlightthickness=1,highlightbackground=outline_collor,highlightcolor=outline_collor,foreground=text_color)
		module01_text01.place(x=105,y=61)
		module01_text02=tk.Entry(root,width=7,validate="key",validatecommand=(vcmd,"%P"),background=light_bg_color,borderwidth=0,highlightthickness=1,highlightbackground=outline_collor,highlightcolor=outline_collor,foreground=text_color)
		module01_text02.place(x=641,y=309)
		module01_arrow00=tk.Button(root,image=I_arrow00,width=59,borderwidth=0,highlightthickness=0,background=dark_bg_color,activebackground=dark_bg_color)
		module01_arrow00.place(x=577,y=246)
		module01_label00 = tk.Label(module01_frame00,text="Cooking Time:",background=light_bg_color,foreground=text_color,highlightthickness=0,width=11)
		module01_label00.place(x=3,y=33)
		module01_label01 = tk.Label(module01_frame00,text="Experience:",background=light_bg_color,foreground=text_color,highlightthickness=0,width=10)
		module01_label01.place(x=0,y=59)				
		module01_select00 = ttk.Combobox(module01_frame00,width=20,values=["minecraft:smelting","minecraft:blasting","minecraft:smoking","minecraft:campfire_cooking"],state="readonly")
		module01_select00.place(x=4,y=6)
		module01_select00.bind("<<ComboboxSelected>>",lambda event:services.update_furnace_type(str(module01_select00.get())))
		module01_text00.bind("<KeyRelease>",update_furnace)
		module01_text01.bind("<KeyRelease>",update_furnace)
		module01_text02.bind("<KeyRelease>",update_furnace)

		element_database = [module01_slot00,module01_slot01,module01_text00,module01_text01,module01_text02,module01_select00,module01_arrow00,module01_frame00,module01_label00,module01_label01]


	if modules == "crafting":#crafting table
		module00_slot00=tk.Button(root,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module00_slot00,1),highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color)
		module00_slot00.place(x=400,y=200)
		module00_slot01=tk.Button(root,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module00_slot01,2),highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color)
		module00_slot01.place(x=455,y=200)
		module00_slot02=tk.Button(root,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module00_slot02,3),highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color)
		module00_slot02.place(x=510,y=200)

		module00_slot03=tk.Button(root,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module00_slot03,4),highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color)
		module00_slot03.place(x=400,y=255)
		module00_slot04=tk.Button(root,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module00_slot04,5),highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color)
		module00_slot04.place(x=455,y=255)
		module00_slot05=tk.Button(root,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module00_slot05,6),highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color)
		module00_slot05.place(x=510,y=255)

		module00_slot06=tk.Button(root,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module00_slot06,7),highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color)
		module00_slot06.place(x=400,y=310)
		module00_slot07=tk.Button(root,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module00_slot07,8),highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color)
		module00_slot07.place(x=455,y=310)
		module00_slot08=tk.Button(root,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module00_slot08,9),highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color)
		module00_slot08.place(x=510,y=310)

		module00_arrow00=tk.Button(root,image=I_arrow00,width=59,borderwidth=0,highlightthickness=0,background=dark_bg_color,activebackground=dark_bg_color)
		module00_arrow00.place(x=574,y=252)
		module00_slot09=tk.Button(root,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module00_slot09,"result"),highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color)
		module00_slot09.place(x=640,y=254)

		module00_text00=tk.Entry(root,width=7,validate="key",validatecommand=(vcmd,"%P"),background=light_bg_color,borderwidth=0,highlightthickness=1,highlightbackground=outline_collor,highlightcolor=outline_collor,foreground=text_color)
		module00_text00.insert(0,1)
		module00_text00.place(x=639,y=314)
		
		module00_text00.bind("<KeyRelease>", lambda event:services.create_crafting_result_count(module00_text00.get()))
		element_database = [
		module00_slot00,module00_slot01,module00_slot02,module00_slot03,module00_slot04,module00_slot05,module00_slot06,module00_slot07,module00_slot08,module00_slot09,module00_text00,
		module00_arrow00]

	if modules == "crafting_shapeless":#crafting table
		module02_slot00=tk.Button(root,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module02_slot00,1),highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color)
		module02_slot00.place(x=400,y=200)
		module02_slot01=tk.Button(root,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module02_slot01,2),highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color)
		module02_slot01.place(x=455,y=200)
		module02_slot02=tk.Button(root,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module02_slot02,3),highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color)
		module02_slot02.place(x=510,y=200)

		module02_slot03=tk.Button(root,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module02_slot03,4),highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color)
		module02_slot03.place(x=400,y=255)
		module02_slot04=tk.Button(root,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module02_slot04,5),highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color)
		module02_slot04.place(x=455,y=255)
		module02_slot05=tk.Button(root,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module02_slot05,6),highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color)
		module02_slot05.place(x=510,y=255)

		module02_slot06=tk.Button(root,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module02_slot06,7),highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color)
		module02_slot06.place(x=400,y=310)
		module02_slot07=tk.Button(root,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module02_slot07,8),highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color)
		module02_slot07.place(x=455,y=310)
		module02_slot08=tk.Button(root,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module02_slot08,9),highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color)
		module02_slot08.place(x=510,y=310)

		module02_arrow00=tk.Button(root,image=I_arrow00,width=59,borderwidth=0,highlightthickness=0,background=dark_bg_color,activebackground=dark_bg_color)
		module02_arrow00.place(x=574,y=252)
		module02_slot09=tk.Button(root,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module02_slot09,"result"),highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color)
		module02_slot09.place(x=640,y=254)

		module02_text00=tk.Entry(root,width=7,validate="key",validatecommand=(vcmd,"%P"),background=light_bg_color,borderwidth=0,highlightthickness=1,highlightbackground=outline_collor,highlightcolor=outline_collor,foreground=text_color)
		module02_text00.insert(0,1)
		module02_text00.place(x=639,y=314)
		
		module02_text00.bind("<KeyRelease>", lambda event:services.create_crafting_result_count(module02_text00.get()))

		element_database = [module02_slot00,module02_slot01,module02_slot02,module02_slot03,module02_slot04,module02_slot05,module02_slot06,module02_slot07,module02_slot08,module02_slot09,module02_text00,module02_arrow00]

	if modules == "pressing":
		module03_slot00 = tk.Button(root,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module03_slot00,"in"),highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color)
		module03_slot00.place(y=179,x=446)
		add_button = tk.Button(root,background=light_bg_color,activebackground=outline_collor,foreground=text_color,activeforeground="#000000",highlightbackground=outline_collor,highlightcolor=outline_collor,highlightthickness=1,text="Add Item",width=46,command=lambda:services.add_result_pressing(update_pressing_result))
		add_button.place(y=454,x=583)

		module03_arrow00=tk.Button(root,image=I_arrow00,width=59,borderwidth=0,highlightthickness=0,background=dark_bg_color,activebackground=dark_bg_color)
		module03_arrow00.place(x=511,y=175)
		main_frame = tk.Frame(root, background=dark_bg_color)
		main_frame.place(x=572,y=163)
		canvas = tk.Canvas(main_frame,background=light_bg_color,highlightbackground=outline_collor,highlightcolor=outline_collor)
		canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1, pady=(10, 10), padx=(10, 0))

		scrollbar = tk.Scrollbar(main_frame, orient=tk.VERTICAL, command=canvas.yview)
		scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=(10, 10), padx=(0, 10))

		canvas.configure(yscrollcommand=scrollbar.set)
		canvas.config(width=375)

		canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

		inner_frame = tk.Frame(canvas,background=light_bg_color)
		canvas.create_window((0, 0), window=inner_frame, anchor="nw")
		element_database = [module03_slot00,main_frame,canvas,scrollbar,add_button]
		def update_pressing_result(results,update_images = False):
			global element_database
			loop = 3
			element_database = [module03_slot00,main_frame,canvas,scrollbar,add_button]
			inputs_count = []
			inputs_chance = []
			input_slot = []
			remove_buttons_elements = []
			titles_elements = []
			for widget in inner_frame.winfo_children():
					widget.destroy()
			for result in results:
				loop = loop + 1
				element_frame = tk.Frame(inner_frame,background=light_bg_color,highlightbackground=outline_collor,highlightcolor=outline_collor,highlightthickness=1)
				element_frame.pack(fill=tk.X, pady=2,padx=(5,0))
				slot = tk.Button(element_frame,image=I_slot00,borderwidth=0,highlightthickness=1,highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color)
				slot.config(command=lambda cl = slot:services.set_result_pressing(cl))
				slot.pack(side=tk.LEFT,padx=(2,2),pady=(2,2))
				slot.result = result
				title00 = tk.Label(element_frame,text="count",width=5,background=light_bg_color,foreground=text_color)
				title00.pack(side=tk.LEFT,padx=(2,0),pady=(2,2))
				text00=tk.Entry(element_frame,width=3,validate="key",validatecommand=(vcmd,"%P"),background=light_bg_color,borderwidth=0,highlightthickness=1,highlightbackground=outline_collor,highlightcolor=outline_collor,foreground=text_color)
				text00.pack(side=tk.LEFT,padx=(1,2),pady=(2,2))
				text00.insert(0,result.get("count"))
				text00.bind("<KeyRelease>", lambda event, vl = text00, cl = slot:services.set_result_pressing_count(vl,cl))
				title02 = tk.Label(element_frame,text="chance",width=6,background=light_bg_color,foreground=text_color)
				title02.pack(side=tk.LEFT,padx=(2,0),pady=(2,2))
				text01=tk.Entry(element_frame,width=3,validate="key",validatecommand=(vcmd,"%P"),background=light_bg_color,borderwidth=0,highlightthickness=1,highlightbackground=outline_collor,highlightcolor=outline_collor,foreground=text_color)
				text01.pack(side=tk.LEFT,padx=(1,2),pady=(2,2))
				text01.insert(0,result.get("chance"))
				text01.bind("<KeyRelease>", lambda event, vl = text01, cl = slot:services.set_result_pressing_chance(vl,cl))
				title03 = tk.Label(element_frame,text="%",width=1,background=light_bg_color,foreground=text_color)
				title03.pack(side=tk.LEFT,padx=(0,2),pady=(2,2))
				remove_button = tk.Button(element_frame,background=light_bg_color,activebackground=outline_collor,foreground=text_color,activeforeground="#000000",highlightbackground=outline_collor,highlightcolor=outline_collor,highlightthickness=1,text="Remove",width=6,command = lambda vl = slot:services.remove_result_pressing(vl,update=update_pressing_result))
				remove_button.pack(side=tk.LEFT,padx=(50,2),pady=(2,2))
				remove_buttons_elements.append(remove_button)
				titles_elements.append(title00)
				titles_elements.append(title02)
				titles_elements.append(title03)
				inputs_chance.append(text01)
				inputs_count.append(text00)
				element_database.append(slot)
				input_slot.append(slot)
			if update_images == True:
				services.update_pressing_slot_images(input_slot)
			element_database = element_database + inputs_count + inputs_chance + remove_buttons_elements + [add_button,module03_arrow00] + titles_elements
			inner_frame.update_idletasks()
			canvas.configure(scrollregion=canvas.bbox("all"))
		update_pressing_result(results)
	if modules == "stonecutting":
		module04_slot00=tk.Button(root,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module04_slot00,"in"),highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color)
		module04_slot00.place(x=510,y=310)

		module04_slot01=tk.Button(root,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module04_slot01,"result"),highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color)
		module04_slot01.place(x=640,y=254)

		module04_text00=tk.Entry(root,width=7,validate="key",validatecommand=(vcmd,"%P"),background=light_bg_color,borderwidth=0,highlightthickness=1,highlightbackground=outline_collor,highlightcolor=outline_collor,foreground=text_color)
		module04_text00.insert(0,1)
		module04_text00.place(x=639,y=314)
		module04_text00.bind("<KeyRelease>", lambda event:services.create_crafting_result_count(module04_text00.get()))

		module04_arrow00=tk.Button(root,image=I_arrow00,width=59,borderwidth=0,highlightthickness=0,background=dark_bg_color,activebackground=dark_bg_color)
		module04_arrow00.place(x=574,y=252)
		element_database = [module04_slot00,module04_slot01,module04_text00,module04_arrow00]
	if modules == "smithing_transform":
		module07_slot00=tk.Button(root,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module07_slot00,"in"),highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color)
		module07_slot00.place(x=446,y=222)

		module07_slot01=tk.Button(root,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module07_slot01,"result"),highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color)
		module07_slot01.place(x=640,y=222)

		module07_slot02=tk.Button(root,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module07_slot02,"inpatern"),highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color)
		module07_slot02.place(x=386,y=222)

		module07_slot03=tk.Button(root,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module07_slot03,"addition"),highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color)
		module07_slot03.place(x=506,y=222)

		module07_arrow00=tk.Button(root,image=I_arrow00,width=59,borderwidth=0,highlightthickness=0,background=dark_bg_color,activebackground=dark_bg_color)
		module07_arrow00.place(x=568,y=222)
		caption(root,text="Template    Source     Upgrade                               Result").place(x=387,y=193)
		element_database = [module07_slot00,module07_slot01,module07_slot02,module07_slot03,module07_arrow00]
	
	if modules == "Custum Json":
		frame = ctk.CTkFrame(root,border_width=0)
		frame.place(x=145,y=5)
		master = ctk.CTkTextbox(frame,width=850,height=560)
		master.pack(fill="both")
		master.configure(tabs=("4m",))
		def check_json_syntax(event=None):
			content = master.get("1.0", "end-1c")
			try:
				json.loads(content)
				master.tag_remove("json_error", "1.0", "end")
			except json.JSONDecodeError as e:
				line, column = e.lineno, e.colno

				start_index = f"{line}.0"
				end_index = f"{line}.end"
				master.tag_add("json_error", start_index, end_index)
				master.tag_config("json_error", background="red", foreground="white")

		object_commander = TextBoxCommander(master)
		object_commander.add_mark_keywords("#C061CB",["{","}"])
		object_commander.add_mark_keywords("#F8E45C",["(",")"])
		object_commander.add_mark_keywords("#3584E4",["[","]"])
		object_commander.add_mark_keywords("#ED333B",["\"","\"","'","'"])
		object_commander.add_mark_keywords("#8FF0A4",["0","1","2","3","4","5","6","7","8","9"])
		master.bind("<KeyPress>",auto_close)
		master.bind("<KeyRelease>",check_json_syntax)

		master.bind("<KeyRelease>",lambda v: services.update_json_text_box(master.get(1.0,ctk.END)))
		
		element_database = [master,frame]
	
	if modules == "create_mixing":
		module00_slot00=tk.Button(root,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.set_mixing_items_ins(module00_slot00,1),highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color)
		module00_slot00.place(x=250,y=40)
		module00_slot01=tk.Button(root,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.set_mixing_items_ins(module00_slot01,2),highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color)
		module00_slot01.place(x=250,y=95)
		module00_slot02=tk.Button(root,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.set_mixing_items_ins(module00_slot02,3),highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color)
		module00_slot02.place(x=250,y=150)

		module00_slot03=tk.Button(root,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.set_mixing_items_ins(module00_slot03,4),highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color)
		module00_slot03.place(x=250,y=205)
		module00_slot04=tk.Button(root,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.set_mixing_items_ins(module00_slot04,5),highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color)
		module00_slot04.place(x=250,y=260)
		module00_slot05=tk.Button(root,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.set_mixing_items_ins(module00_slot05,6),highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color)
		module00_slot05.place(x=250,y=315)

		module00_slot06=tk.Button(root,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.set_mixing_items_ins(module00_slot06,7),highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color)
		module00_slot06.place(x=250,y=370)
		module00_slot07=tk.Button(root,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.set_mixing_items_ins(module00_slot07,8),highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color)
		module00_slot07.place(x=250,y=425)
		module00_slot08=tk.Button(root,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.set_mixing_items_ins(module00_slot08,9),highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color)
		module00_slot08.place(x=250,y=480)

		module00_slot09=tk.Button(root,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.set_mixing_items_results(module00_slot09,1),highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color)
		module00_slot09.place(x=600,y=40)
		module00_slot10=tk.Button(root,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.set_mixing_items_results(module00_slot10,2),highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color)
		module00_slot10.place(x=600,y=95)
		module00_slot11=tk.Button(root,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.set_mixing_items_results(module00_slot11,3),highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color)
		module00_slot11.place(x=600,y=150)

		module00_slot12=tk.Button(root,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.set_mixing_items_results(module00_slot12,4),highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color)
		module00_slot12.place(x=600,y=205)
		module00_slot13=tk.Button(root,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.set_mixing_items_results(module00_slot13,5),highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color)
		module00_slot13.place(x=600,y=260)
		module00_slot14=tk.Button(root,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.set_mixing_items_results(module00_slot14,6),highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color)
		module00_slot14.place(x=600,y=315)

		module00_slot15=tk.Button(root,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.set_mixing_items_results(module00_slot15,7),highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color)
		module00_slot15.place(x=600,y=370)
		module00_slot16=tk.Button(root,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.set_mixing_items_results(module00_slot16,8),highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color)
		module00_slot16.place(x=600,y=425)
		module00_slot17=tk.Button(root,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.set_mixing_items_results(module00_slot17,9),highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color)
		module00_slot17.place(x=600,y=480)

		#count inputs
		def valide_input(value):
			if value == "":
				return True
			if value.isdigit():
				return True
			return False
		#vcmd = (root.register(valide_input), '%P')

		start_x1, start_x2 = 310, 660  # Výchozí x-ové souřadnice pro dva sloupce
		start_y = 45  # Výchozí y-ová souřadnice
		offset_y = 55  # Vertikální posun mezi Entry widgety

		module00_input00 = tk.Entry(root, width=7, validate="key", validatecommand=(vcmd, "%P"),
									background=light_bg_color, borderwidth=0, highlightthickness=1,
									highlightbackground=outline_collor, highlightcolor=outline_collor,
									foreground=text_color)
		module00_input00.insert(0, 1)
		module00_input00.place(x=start_x1, y=start_y + 0 * offset_y)

		module00_input01 = tk.Entry(root, width=7, validate="key", validatecommand=(vcmd, "%P"),
									background=light_bg_color, borderwidth=0, highlightthickness=1,
									highlightbackground=outline_collor, highlightcolor=outline_collor,
									foreground=text_color)
		module00_input01.insert(0, 1)
		module00_input01.place(x=start_x1, y=start_y + 1 * offset_y)

		module00_input02 = tk.Entry(root, width=7, validate="key", validatecommand=(vcmd, "%P"),
									background=light_bg_color, borderwidth=0, highlightthickness=1,
									highlightbackground=outline_collor, highlightcolor=outline_collor,
									foreground=text_color)
		module00_input02.insert(0, 1)
		module00_input02.place(x=start_x1, y=start_y + 2 * offset_y)

		module00_input03 = tk.Entry(root, width=7, validate="key", validatecommand=(vcmd, "%P"),
									background=light_bg_color, borderwidth=0, highlightthickness=1,
									highlightbackground=outline_collor, highlightcolor=outline_collor,
									foreground=text_color)
		module00_input03.insert(0, 1)
		module00_input03.place(x=start_x1, y=start_y + 3 * offset_y)

		module00_input04 = tk.Entry(root, width=7, validate="key", validatecommand=(vcmd, "%P"),
									background=light_bg_color, borderwidth=0, highlightthickness=1,
									highlightbackground=outline_collor, highlightcolor=outline_collor,
									foreground=text_color)
		module00_input04.insert(0, 1)
		module00_input04.place(x=start_x1, y=start_y + 4 * offset_y)

		module00_input05 = tk.Entry(root, width=7, validate="key", validatecommand=(vcmd, "%P"),
									background=light_bg_color, borderwidth=0, highlightthickness=1,
									highlightbackground=outline_collor, highlightcolor=outline_collor,
									foreground=text_color)
		module00_input05.insert(0, 1)
		module00_input05.place(x=start_x1, y=start_y + 5 * offset_y)

		module00_input06 = tk.Entry(root, width=7, validate="key", validatecommand=(vcmd, "%P"),
									background=light_bg_color, borderwidth=0, highlightthickness=1,
									highlightbackground=outline_collor, highlightcolor=outline_collor,
									foreground=text_color)
		module00_input06.insert(0, 1)
		module00_input06.place(x=start_x1, y=start_y + 6 * offset_y)

		module00_input07 = tk.Entry(root, width=7, validate="key", validatecommand=(vcmd, "%P"),
									background=light_bg_color, borderwidth=0, highlightthickness=1,
									highlightbackground=outline_collor, highlightcolor=outline_collor,
									foreground=text_color)
		module00_input07.insert(0, 1)
		module00_input07.place(x=start_x1, y=start_y + 7 * offset_y)

		module00_input08 = tk.Entry(root, width=7, validate="key", validatecommand=(vcmd, "%P"),
									background=light_bg_color, borderwidth=0, highlightthickness=1,
									highlightbackground=outline_collor, highlightcolor=outline_collor,
									foreground=text_color)
		module00_input08.insert(0, 1)
		module00_input08.place(x=start_x1, y=start_y + 8 * offset_y)

		module00_input09 = tk.Entry(root, width=7, validate="key", validatecommand=(vcmd, "%P"),
									background=light_bg_color, borderwidth=0, highlightthickness=1,
									highlightbackground=outline_collor, highlightcolor=outline_collor,
									foreground=text_color)
		module00_input09.insert(0, 1)
		module00_input09.place(x=start_x2, y=start_y + 0 * offset_y)

		module00_input10 = tk.Entry(root, width=7, validate="key", validatecommand=(vcmd, "%P"),
									background=light_bg_color, borderwidth=0, highlightthickness=1,
									highlightbackground=outline_collor, highlightcolor=outline_collor,
									foreground=text_color)
		module00_input10.insert(0, 1)
		module00_input10.place(x=start_x2, y=start_y + 1 * offset_y)

		module00_input11 = tk.Entry(root, width=7, validate="key", validatecommand=(vcmd, "%P"),
									background=light_bg_color, borderwidth=0, highlightthickness=1,
									highlightbackground=outline_collor, highlightcolor=outline_collor,
									foreground=text_color)
		module00_input11.insert(0, 1)
		module00_input11.place(x=start_x2, y=start_y + 2 * offset_y)

		module00_input12 = tk.Entry(root, width=7, validate="key", validatecommand=(vcmd, "%P"),
									background=light_bg_color, borderwidth=0, highlightthickness=1,
									highlightbackground=outline_collor, highlightcolor=outline_collor,
									foreground=text_color)
		module00_input12.insert(0, 1)
		module00_input12.place(x=start_x2, y=start_y + 3 * offset_y)

		module00_input13 = tk.Entry(root, width=7, validate="key", validatecommand=(vcmd, "%P"),
									background=light_bg_color, borderwidth=0, highlightthickness=1,
									highlightbackground=outline_collor, highlightcolor=outline_collor,
									foreground=text_color)
		module00_input13.insert(0, 1)
		module00_input13.place(x=start_x2, y=start_y + 4 * offset_y)

		module00_input14 = tk.Entry(root, width=7, validate="key", validatecommand=(vcmd, "%P"),
									background=light_bg_color, borderwidth=0, highlightthickness=1,
									highlightbackground=outline_collor, highlightcolor=outline_collor,
									foreground=text_color)
		module00_input14.insert(0, 1)
		module00_input14.place(x=start_x2, y=start_y + 5 * offset_y)

		module00_input15 = tk.Entry(root, width=7, validate="key", validatecommand=(vcmd, "%P"),
									background=light_bg_color, borderwidth=0, highlightthickness=1,
									highlightbackground=outline_collor, highlightcolor=outline_collor,
									foreground=text_color)
		module00_input15.insert(0, 1)
		module00_input15.place(x=start_x2, y=start_y + 6 * offset_y)

		module00_input16 = tk.Entry(root, width=7, validate="key", validatecommand=(vcmd, "%P"),
									background=light_bg_color, borderwidth=0, highlightthickness=1,
									highlightbackground=outline_collor, highlightcolor=outline_collor,
									foreground=text_color)
		module00_input16.insert(0, 1)
		module00_input16.place(x=start_x2, y=start_y + 7 * offset_y)

		module00_input17 = tk.Entry(root, width=7, validate="key", validatecommand=(vcmd, "%P"),
									background=light_bg_color, borderwidth=0, highlightthickness=1,
									highlightbackground=outline_collor, highlightcolor=outline_collor,
									foreground=text_color)
		module00_input17.insert(0, 1)
		module00_input17.place(x=start_x2, y=start_y + 8 * offset_y)

		start_x = 725  # Výchozí pozice x
		start_y = 45  # Výchozí pozice y
		offset = 55	# Posun mezi jednotlivými widgety

		module00_input18 = tk.Entry(root, width=7, validate="key", validatecommand=vcmd,
									background=light_bg_color, borderwidth=0, highlightthickness=1,
									highlightbackground=outline_collor, highlightcolor=outline_collor, 
									foreground=text_color)
		module00_input18.insert(0, 1)
		module00_input18.place(x=start_x, y=start_y)  # Nový widget

		module00_input19 = tk.Entry(root, width=7, validate="key", validatecommand=vcmd,
									background=light_bg_color, borderwidth=0, highlightthickness=1,
									highlightbackground=outline_collor, highlightcolor=outline_collor, 
									foreground=text_color)
		module00_input19.insert(0, 1)
		module00_input19.place(x=start_x, y=start_y + offset)  # Nový widget

		module00_input20 = tk.Entry(root, width=7, validate="key", validatecommand=vcmd,
									background=light_bg_color, borderwidth=0, highlightthickness=1,
									highlightbackground=outline_collor, highlightcolor=outline_collor, 
									foreground=text_color)
		module00_input20.insert(0, 1)
		module00_input20.place(x=start_x, y=start_y + 2 * offset)  # Nový widget

		module00_input21 = tk.Entry(root, width=7, validate="key", validatecommand=vcmd,
									background=light_bg_color, borderwidth=0, highlightthickness=1,
									highlightbackground=outline_collor, highlightcolor=outline_collor, 
									foreground=text_color)
		module00_input21.insert(0, 1)
		module00_input21.place(x=start_x, y=start_y + 3 * offset)  # Nový widget

		module00_input22 = tk.Entry(root, width=7, validate="key", validatecommand=vcmd,
									background=light_bg_color, borderwidth=0, highlightthickness=1,
									highlightbackground=outline_collor, highlightcolor=outline_collor, 
									foreground=text_color)
		module00_input22.insert(0, 1)
		module00_input22.place(x=start_x, y=start_y + 4 * offset)  # Nový widget

		module00_input23 = tk.Entry(root, width=7, validate="key", validatecommand=vcmd,
									background=light_bg_color, borderwidth=0, highlightthickness=1,
									highlightbackground=outline_collor, highlightcolor=outline_collor, 
									foreground=text_color)
		module00_input23.insert(0, 1)
		module00_input23.place(x=start_x, y=start_y + 5 * offset)  # Nový widget

		module00_input24 = tk.Entry(root, width=7, validate="key", validatecommand=vcmd,
									background=light_bg_color, borderwidth=0, highlightthickness=1,
									highlightbackground=outline_collor, highlightcolor=outline_collor, 
									foreground=text_color)
		module00_input24.insert(0, 1)
		module00_input24.place(x=start_x, y=start_y + 6 * offset)  # Nový widget

		module00_input25 = tk.Entry(root, width=7, validate="key", validatecommand=vcmd,
									background=light_bg_color, borderwidth=0, highlightthickness=1,
									highlightbackground=outline_collor, highlightcolor=outline_collor, 
									foreground=text_color)
		module00_input25.insert(0, 1)
		module00_input25.place(x=start_x, y=start_y + 7 * offset)  # Nový widget

		module00_input26 = tk.Entry(root, width=7, validate="key", validatecommand=vcmd,
									background=light_bg_color, borderwidth=0, highlightthickness=1,
									highlightbackground=outline_collor, highlightcolor=outline_collor, 
									foreground=text_color)
		module00_input26.insert(0, 1)
		module00_input26.place(x=start_x, y=start_y + 8 * offset)  # Nový widget


		module00_input00.bind("<KeyRelease>", lambda event: services.set_mixing_ins_counts(module00_input00.get(), 1))
		module00_input01.bind("<KeyRelease>", lambda event: services.set_mixing_ins_counts(module00_input01.get(), 2))
		module00_input02.bind("<KeyRelease>", lambda event: services.set_mixing_ins_counts(module00_input02.get(), 3))
		module00_input03.bind("<KeyRelease>", lambda event: services.set_mixing_ins_counts(module00_input03.get(), 4))
		module00_input04.bind("<KeyRelease>", lambda event: services.set_mixing_ins_counts(module00_input04.get(), 5))
		module00_input05.bind("<KeyRelease>", lambda event: services.set_mixing_ins_counts(module00_input05.get(), 6))
		module00_input06.bind("<KeyRelease>", lambda event: services.set_mixing_ins_counts(module00_input06.get(), 7))
		module00_input07.bind("<KeyRelease>", lambda event: services.set_mixing_ins_counts(module00_input07.get(), 8))
		module00_input08.bind("<KeyRelease>", lambda event: services.set_mixing_ins_counts(module00_input08.get(), 9))
		
		module00_input09.bind("<KeyRelease>", lambda event: services.set_mixing_results_counts(module00_input09.get(), 1))
		module00_input10.bind("<KeyRelease>", lambda event: services.set_mixing_results_counts(module00_input10.get(), 2))
		module00_input11.bind("<KeyRelease>", lambda event: services.set_mixing_results_counts(module00_input11.get(), 3))
		module00_input12.bind("<KeyRelease>", lambda event: services.set_mixing_results_counts(module00_input12.get(), 4))
		module00_input13.bind("<KeyRelease>", lambda event: services.set_mixing_results_counts(module00_input13.get(), 5))
		module00_input14.bind("<KeyRelease>", lambda event: services.set_mixing_results_counts(module00_input14.get(), 6))
		module00_input15.bind("<KeyRelease>", lambda event: services.set_mixing_results_counts(module00_input15.get(), 7))
		module00_input16.bind("<KeyRelease>", lambda event: services.set_mixing_results_counts(module00_input16.get(), 8))
		module00_input17.bind("<KeyRelease>", lambda event: services.set_mixing_results_counts(module00_input17.get(), 9))

		module00_input18.bind("<KeyRelease>", lambda event: services.set_mixing_results_chance(module00_input18.get(), 1))
		module00_input19.bind("<KeyRelease>", lambda event: services.set_mixing_results_chance(module00_input19.get(), 2))
		module00_input20.bind("<KeyRelease>", lambda event: services.set_mixing_results_chance(module00_input20.get(), 3))
		module00_input21.bind("<KeyRelease>", lambda event: services.set_mixing_results_chance(module00_input21.get(), 4))
		module00_input22.bind("<KeyRelease>", lambda event: services.set_mixing_results_chance(module00_input22.get(), 5))
		module00_input23.bind("<KeyRelease>", lambda event: services.set_mixing_results_chance(module00_input23.get(), 6))
		module00_input24.bind("<KeyRelease>", lambda event: services.set_mixing_results_chance(module00_input24.get(), 7))
		module00_input25.bind("<KeyRelease>", lambda event: services.set_mixing_results_chance(module00_input25.get(), 8))
		module00_input26.bind("<KeyRelease>", lambda event: services.set_mixing_results_chance(module00_input26.get(), 9))


		#fluids
		module00_slot18=tk.Button(root,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.set_mixing_fluids(module00_slot18,"ins_fluid1"),highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color)
		module00_slot18.place(x=375,y=40)
		module00_slot19=tk.Button(root,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.set_mixing_fluids(module00_slot19,"ins_fluid2"),highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color)
		module00_slot19.place(x=375,y=95)
		module00_slot20=tk.Button(root,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.set_mixing_fluids(module00_slot20,"results_fluids1"),highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color)
		module00_slot20.place(x=790,y=40)
		module00_slot21=tk.Button(root,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.set_mixing_fluids(module00_slot21,"results_fluids2"),highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color)
		module00_slot21.place(x=790,y=95)


		module00_input27 = tk.Entry(root, width=7, validate="key", validatecommand=vcmd,
									background=light_bg_color, borderwidth=0, highlightthickness=1,
									highlightbackground=outline_collor, highlightcolor=outline_collor, 
									foreground=text_color)
		module00_input27.insert(0, 1)
		module00_input27.place(x=435, y=45)  # Nový widget

		module00_input28 = tk.Entry(root, width=7, validate="key", validatecommand=vcmd,
									background=light_bg_color, borderwidth=0, highlightthickness=1,
									highlightbackground=outline_collor, highlightcolor=outline_collor, 
									foreground=text_color)
		module00_input28.insert(0, 1)
		module00_input28.place(x=435, y=100)  # Nový widget

		module00_input29 = tk.Entry(root, width=7, validate="key", validatecommand=vcmd,
									background=light_bg_color, borderwidth=0, highlightthickness=1,
									highlightbackground=outline_collor, highlightcolor=outline_collor, 
									foreground=text_color)
		module00_input29.insert(0, 1)
		module00_input29.place(x=850, y=45)  # Nový widget

		module00_input30 = tk.Entry(root, width=7, validate="key", validatecommand=vcmd,
									background=light_bg_color, borderwidth=0, highlightthickness=1,
									highlightbackground=outline_collor, highlightcolor=outline_collor, 
									foreground=text_color)
		module00_input30.insert(0, 1)
		#module00_input30.place(x=915, y=45)  # Nový widget

		module00_input31 = tk.Entry(root, width=7, validate="key", validatecommand=vcmd,
									background=light_bg_color, borderwidth=0, highlightthickness=1,
									highlightbackground=outline_collor, highlightcolor=outline_collor, 
									foreground=text_color)
		module00_input31.place(x=850, y=100)
		module00_input31.insert(0,1)  # Nový widget

		module00_input32 = tk.Entry(root, width=7, validate="key", validatecommand=vcmd,
									background=light_bg_color, borderwidth=0, highlightthickness=1,
									highlightbackground=outline_collor, highlightcolor=outline_collor, 
									foreground=text_color)
		module00_input32.insert(0, 1)
		#module00_input32.place(x=915, y=100)  # Nový widget



		module00_input27.bind("<KeyRelease>", lambda event: services.set_fluids_parms(1,module00_input27.get()))
		module00_input28.bind("<KeyRelease>", lambda event: services.set_fluids_parms(2,module00_input28.get()))
		module00_input29.bind("<KeyRelease>", lambda event: services.set_fluids_parms(3,module00_input29.get()))
		module00_input30.bind("<KeyRelease>", lambda event: services.set_fluids_parms(4,module00_input30.get()))
		module00_input31.bind("<KeyRelease>", lambda event: services.set_fluids_parms(5,module00_input31.get()))
		module00_input32.bind("<KeyRelease>", lambda event: services.set_fluids_parms(6,module00_input32.get()))

		module00_select00 = ttk.Combobox(root,width=10,values=["none","heated","superheated"],state="readonly")
		module00_select00.place(x=500,y=44)
		module00_select00.bind("<<ComboboxSelected>>",lambda event:services.update_mixing_hate(str(module00_select00.get())))



		#labels
		label01 = tk.Label(root,text="Count",foreground=text_color,background=dark_bg_color,font=underlined_font0)
		label01.place(x=310,y=20)
		label02 = tk.Label(root,text="Count",foreground=text_color,background=dark_bg_color,font=underlined_font0)
		label02.place(x=660,y=20)
		label03 = tk.Label(root,text="Chance",foreground=text_color,background=dark_bg_color,font=underlined_font0)
		label03.place(x=725,y=20)

		label04 = tk.Label(root,text="Amaunt",foreground=text_color,background=dark_bg_color,font=underlined_font0)
		label04.place(x=435,y=20)
		label05 = tk.Label(root,text="Heat Level",foreground=text_color,background=dark_bg_color,font=underlined_font0)
		label05.place(x=500,y=20)
		label06 = tk.Label(root,text="Amaunt",foreground=text_color,background=dark_bg_color,font=underlined_font0)
		label06.place(x=850,y=20)
		label07 = tk.Label(root,text="Chance",foreground=text_color,background=dark_bg_color,font=underlined_font0)
		#label07.place(x=915,y=20)

		element_database = [
			module00_slot00, module00_slot01, module00_slot02, module00_slot03,
			module00_slot04, module00_slot05, module00_slot06, module00_slot07,
			module00_slot08, module00_slot09, module00_slot10, module00_slot11,
			module00_slot12, module00_slot13, module00_slot14, module00_slot15,
			module00_slot16, module00_slot17, module00_slot18, module00_slot19,
			module00_slot20, module00_slot21,module00_input00,module00_input01,
			module00_input02,module00_input03,module00_input04,module00_input05,
			module00_input06,module00_input07,module00_input08,module00_input09,
			module00_input10,module00_input11,module00_input12,module00_input13,
			module00_input14,module00_input15,module00_input16,module00_input17,
			module00_input18, module00_input19, module00_input20, module00_input21,
			module00_input22, module00_input23, module00_input24, module00_input25,
			module00_input26, module00_input27, module00_input28, module00_input29,
			module00_input30, module00_input31, module00_input32, module00_select00
			] + [label01,label02,label03,label04,label05,label06,label07]

	if modules == "create_compacting":
		module00_slot00=tk.Button(root,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.set_mixing_items_ins(module00_slot00,1),highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color)
		module00_slot00.place(x=250,y=40)
		module00_slot01=tk.Button(root,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.set_mixing_items_ins(module00_slot01,2),highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color)
		module00_slot01.place(x=250,y=95)
		module00_slot02=tk.Button(root,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.set_mixing_items_ins(module00_slot02,3),highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color)
		module00_slot02.place(x=250,y=150)

		module00_slot03=tk.Button(root,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.set_mixing_items_ins(module00_slot03,4),highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color)
		module00_slot03.place(x=250,y=205)
		module00_slot04=tk.Button(root,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.set_mixing_items_ins(module00_slot04,5),highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color)
		module00_slot04.place(x=250,y=260)
		module00_slot05=tk.Button(root,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.set_mixing_items_ins(module00_slot05,6),highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color)
		module00_slot05.place(x=250,y=315)

		module00_slot06=tk.Button(root,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.set_mixing_items_ins(module00_slot06,7),highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color)
		module00_slot06.place(x=250,y=370)
		module00_slot07=tk.Button(root,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.set_mixing_items_ins(module00_slot07,8),highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color)
		module00_slot07.place(x=250,y=425)
		module00_slot08=tk.Button(root,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.set_mixing_items_ins(module00_slot08,9),highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color)
		module00_slot08.place(x=250,y=480)

		module00_slot09=tk.Button(root,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.set_mixing_items_results(module00_slot09,1),highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color)
		module00_slot09.place(x=600,y=40)
		module00_slot10=tk.Button(root,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.set_mixing_items_results(module00_slot10,2),highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color)
		module00_slot10.place(x=600,y=95)
		module00_slot11=tk.Button(root,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.set_mixing_items_results(module00_slot11,3),highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color)
		module00_slot11.place(x=600,y=150)

		module00_slot12=tk.Button(root,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.set_mixing_items_results(module00_slot12,4),highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color)
		module00_slot12.place(x=600,y=205)
		module00_slot13=tk.Button(root,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.set_mixing_items_results(module00_slot13,5),highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color)
		module00_slot13.place(x=600,y=260)
		module00_slot14=tk.Button(root,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.set_mixing_items_results(module00_slot14,6),highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color)
		module00_slot14.place(x=600,y=315)

		module00_slot15=tk.Button(root,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.set_mixing_items_results(module00_slot15,7),highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color)
		module00_slot15.place(x=600,y=370)
		module00_slot16=tk.Button(root,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.set_mixing_items_results(module00_slot16,8),highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color)
		module00_slot16.place(x=600,y=425)
		module00_slot17=tk.Button(root,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.set_mixing_items_results(module00_slot17,9),highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color)
		module00_slot17.place(x=600,y=480)

		#count inputs
		def valide_input(value):
			if value == "":
				return True
			if value.isdigit():
				return True
			return False
		#vcmd = (root.register(valide_input), '%P')

		start_x1, start_x2 = 310, 660  # Výchozí x-ové souřadnice pro dva sloupce
		start_y = 45  # Výchozí y-ová souřadnice
		offset_y = 55  # Vertikální posun mezi Entry widgety

		module00_input00 = tk.Entry(root, width=7, validate="key", validatecommand=(vcmd, "%P"),
									background=light_bg_color, borderwidth=0, highlightthickness=1,
									highlightbackground=outline_collor, highlightcolor=outline_collor,
									foreground=text_color)
		module00_input00.insert(0, 1)
		module00_input00.place(x=start_x1, y=start_y + 0 * offset_y)

		module00_input01 = tk.Entry(root, width=7, validate="key", validatecommand=(vcmd, "%P"),
									background=light_bg_color, borderwidth=0, highlightthickness=1,
									highlightbackground=outline_collor, highlightcolor=outline_collor,
									foreground=text_color)
		module00_input01.insert(0, 1)
		module00_input01.place(x=start_x1, y=start_y + 1 * offset_y)

		module00_input02 = tk.Entry(root, width=7, validate="key", validatecommand=(vcmd, "%P"),
									background=light_bg_color, borderwidth=0, highlightthickness=1,
									highlightbackground=outline_collor, highlightcolor=outline_collor,
									foreground=text_color)
		module00_input02.insert(0, 1)
		module00_input02.place(x=start_x1, y=start_y + 2 * offset_y)

		module00_input03 = tk.Entry(root, width=7, validate="key", validatecommand=(vcmd, "%P"),
									background=light_bg_color, borderwidth=0, highlightthickness=1,
									highlightbackground=outline_collor, highlightcolor=outline_collor,
									foreground=text_color)
		module00_input03.insert(0, 1)
		module00_input03.place(x=start_x1, y=start_y + 3 * offset_y)

		module00_input04 = tk.Entry(root, width=7, validate="key", validatecommand=(vcmd, "%P"),
									background=light_bg_color, borderwidth=0, highlightthickness=1,
									highlightbackground=outline_collor, highlightcolor=outline_collor,
									foreground=text_color)
		module00_input04.insert(0, 1)
		module00_input04.place(x=start_x1, y=start_y + 4 * offset_y)

		module00_input05 = tk.Entry(root, width=7, validate="key", validatecommand=(vcmd, "%P"),
									background=light_bg_color, borderwidth=0, highlightthickness=1,
									highlightbackground=outline_collor, highlightcolor=outline_collor,
									foreground=text_color)
		module00_input05.insert(0, 1)
		module00_input05.place(x=start_x1, y=start_y + 5 * offset_y)

		module00_input06 = tk.Entry(root, width=7, validate="key", validatecommand=(vcmd, "%P"),
									background=light_bg_color, borderwidth=0, highlightthickness=1,
									highlightbackground=outline_collor, highlightcolor=outline_collor,
									foreground=text_color)
		module00_input06.insert(0, 1)
		module00_input06.place(x=start_x1, y=start_y + 6 * offset_y)

		module00_input07 = tk.Entry(root, width=7, validate="key", validatecommand=(vcmd, "%P"),
									background=light_bg_color, borderwidth=0, highlightthickness=1,
									highlightbackground=outline_collor, highlightcolor=outline_collor,
									foreground=text_color)
		module00_input07.insert(0, 1)
		module00_input07.place(x=start_x1, y=start_y + 7 * offset_y)

		module00_input08 = tk.Entry(root, width=7, validate="key", validatecommand=(vcmd, "%P"),
									background=light_bg_color, borderwidth=0, highlightthickness=1,
									highlightbackground=outline_collor, highlightcolor=outline_collor,
									foreground=text_color)
		module00_input08.insert(0, 1)
		module00_input08.place(x=start_x1, y=start_y + 8 * offset_y)

		module00_input09 = tk.Entry(root, width=7, validate="key", validatecommand=(vcmd, "%P"),
									background=light_bg_color, borderwidth=0, highlightthickness=1,
									highlightbackground=outline_collor, highlightcolor=outline_collor,
									foreground=text_color)
		module00_input09.insert(0, 1)
		module00_input09.place(x=start_x2, y=start_y + 0 * offset_y)

		module00_input10 = tk.Entry(root, width=7, validate="key", validatecommand=(vcmd, "%P"),
									background=light_bg_color, borderwidth=0, highlightthickness=1,
									highlightbackground=outline_collor, highlightcolor=outline_collor,
									foreground=text_color)
		module00_input10.insert(0, 1)
		module00_input10.place(x=start_x2, y=start_y + 1 * offset_y)

		module00_input11 = tk.Entry(root, width=7, validate="key", validatecommand=(vcmd, "%P"),
									background=light_bg_color, borderwidth=0, highlightthickness=1,
									highlightbackground=outline_collor, highlightcolor=outline_collor,
									foreground=text_color)
		module00_input11.insert(0, 1)
		module00_input11.place(x=start_x2, y=start_y + 2 * offset_y)

		module00_input12 = tk.Entry(root, width=7, validate="key", validatecommand=(vcmd, "%P"),
									background=light_bg_color, borderwidth=0, highlightthickness=1,
									highlightbackground=outline_collor, highlightcolor=outline_collor,
									foreground=text_color)
		module00_input12.insert(0, 1)
		module00_input12.place(x=start_x2, y=start_y + 3 * offset_y)

		module00_input13 = tk.Entry(root, width=7, validate="key", validatecommand=(vcmd, "%P"),
									background=light_bg_color, borderwidth=0, highlightthickness=1,
									highlightbackground=outline_collor, highlightcolor=outline_collor,
									foreground=text_color)
		module00_input13.insert(0, 1)
		module00_input13.place(x=start_x2, y=start_y + 4 * offset_y)

		module00_input14 = tk.Entry(root, width=7, validate="key", validatecommand=(vcmd, "%P"),
									background=light_bg_color, borderwidth=0, highlightthickness=1,
									highlightbackground=outline_collor, highlightcolor=outline_collor,
									foreground=text_color)
		module00_input14.insert(0, 1)
		module00_input14.place(x=start_x2, y=start_y + 5 * offset_y)

		module00_input15 = tk.Entry(root, width=7, validate="key", validatecommand=(vcmd, "%P"),
									background=light_bg_color, borderwidth=0, highlightthickness=1,
									highlightbackground=outline_collor, highlightcolor=outline_collor,
									foreground=text_color)
		module00_input15.insert(0, 1)
		module00_input15.place(x=start_x2, y=start_y + 6 * offset_y)

		module00_input16 = tk.Entry(root, width=7, validate="key", validatecommand=(vcmd, "%P"),
									background=light_bg_color, borderwidth=0, highlightthickness=1,
									highlightbackground=outline_collor, highlightcolor=outline_collor,
									foreground=text_color)
		module00_input16.insert(0, 1)
		module00_input16.place(x=start_x2, y=start_y + 7 * offset_y)

		module00_input17 = tk.Entry(root, width=7, validate="key", validatecommand=(vcmd, "%P"),
									background=light_bg_color, borderwidth=0, highlightthickness=1,
									highlightbackground=outline_collor, highlightcolor=outline_collor,
									foreground=text_color)
		module00_input17.insert(0, 1)
		module00_input17.place(x=start_x2, y=start_y + 8 * offset_y)

		start_x = 725  # Výchozí pozice x
		start_y = 45  # Výchozí pozice y
		offset = 55	# Posun mezi jednotlivými widgety

		module00_input18 = tk.Entry(root, width=7, validate="key", validatecommand=vcmd,
									background=light_bg_color, borderwidth=0, highlightthickness=1,
									highlightbackground=outline_collor, highlightcolor=outline_collor, 
									foreground=text_color)
		module00_input18.insert(0, 1)
		module00_input18.place(x=start_x, y=start_y)  # Nový widget

		module00_input19 = tk.Entry(root, width=7, validate="key", validatecommand=vcmd,
									background=light_bg_color, borderwidth=0, highlightthickness=1,
									highlightbackground=outline_collor, highlightcolor=outline_collor, 
									foreground=text_color)
		module00_input19.insert(0, 1)
		module00_input19.place(x=start_x, y=start_y + offset)  # Nový widget

		module00_input20 = tk.Entry(root, width=7, validate="key", validatecommand=vcmd,
									background=light_bg_color, borderwidth=0, highlightthickness=1,
									highlightbackground=outline_collor, highlightcolor=outline_collor, 
									foreground=text_color)
		module00_input20.insert(0, 1)
		module00_input20.place(x=start_x, y=start_y + 2 * offset)  # Nový widget

		module00_input21 = tk.Entry(root, width=7, validate="key", validatecommand=vcmd,
									background=light_bg_color, borderwidth=0, highlightthickness=1,
									highlightbackground=outline_collor, highlightcolor=outline_collor, 
									foreground=text_color)
		module00_input21.insert(0, 1)
		module00_input21.place(x=start_x, y=start_y + 3 * offset)  # Nový widget

		module00_input22 = tk.Entry(root, width=7, validate="key", validatecommand=vcmd,
									background=light_bg_color, borderwidth=0, highlightthickness=1,
									highlightbackground=outline_collor, highlightcolor=outline_collor, 
									foreground=text_color)
		module00_input22.insert(0, 1)
		module00_input22.place(x=start_x, y=start_y + 4 * offset)  # Nový widget

		module00_input23 = tk.Entry(root, width=7, validate="key", validatecommand=vcmd,
									background=light_bg_color, borderwidth=0, highlightthickness=1,
									highlightbackground=outline_collor, highlightcolor=outline_collor, 
									foreground=text_color)
		module00_input23.insert(0, 1)
		module00_input23.place(x=start_x, y=start_y + 5 * offset)  # Nový widget

		module00_input24 = tk.Entry(root, width=7, validate="key", validatecommand=vcmd,
									background=light_bg_color, borderwidth=0, highlightthickness=1,
									highlightbackground=outline_collor, highlightcolor=outline_collor, 
									foreground=text_color)
		module00_input24.insert(0, 1)
		module00_input24.place(x=start_x, y=start_y + 6 * offset)  # Nový widget

		module00_input25 = tk.Entry(root, width=7, validate="key", validatecommand=vcmd,
									background=light_bg_color, borderwidth=0, highlightthickness=1,
									highlightbackground=outline_collor, highlightcolor=outline_collor, 
									foreground=text_color)
		module00_input25.insert(0, 1)
		module00_input25.place(x=start_x, y=start_y + 7 * offset)  # Nový widget

		module00_input26 = tk.Entry(root, width=7, validate="key", validatecommand=vcmd,
									background=light_bg_color, borderwidth=0, highlightthickness=1,
									highlightbackground=outline_collor, highlightcolor=outline_collor, 
									foreground=text_color)
		module00_input26.insert(0, 1)
		module00_input26.place(x=start_x, y=start_y + 8 * offset)  # Nový widget


		module00_input00.bind("<KeyRelease>", lambda event: services.set_mixing_ins_counts(module00_input00.get(), 1))
		module00_input01.bind("<KeyRelease>", lambda event: services.set_mixing_ins_counts(module00_input01.get(), 2))
		module00_input02.bind("<KeyRelease>", lambda event: services.set_mixing_ins_counts(module00_input02.get(), 3))
		module00_input03.bind("<KeyRelease>", lambda event: services.set_mixing_ins_counts(module00_input03.get(), 4))
		module00_input04.bind("<KeyRelease>", lambda event: services.set_mixing_ins_counts(module00_input04.get(), 5))
		module00_input05.bind("<KeyRelease>", lambda event: services.set_mixing_ins_counts(module00_input05.get(), 6))
		module00_input06.bind("<KeyRelease>", lambda event: services.set_mixing_ins_counts(module00_input06.get(), 7))
		module00_input07.bind("<KeyRelease>", lambda event: services.set_mixing_ins_counts(module00_input07.get(), 8))
		module00_input08.bind("<KeyRelease>", lambda event: services.set_mixing_ins_counts(module00_input08.get(), 9))
		
		module00_input09.bind("<KeyRelease>", lambda event: services.set_mixing_results_counts(module00_input09.get(), 1))
		module00_input10.bind("<KeyRelease>", lambda event: services.set_mixing_results_counts(module00_input10.get(), 2))
		module00_input11.bind("<KeyRelease>", lambda event: services.set_mixing_results_counts(module00_input11.get(), 3))
		module00_input12.bind("<KeyRelease>", lambda event: services.set_mixing_results_counts(module00_input12.get(), 4))
		module00_input13.bind("<KeyRelease>", lambda event: services.set_mixing_results_counts(module00_input13.get(), 5))
		module00_input14.bind("<KeyRelease>", lambda event: services.set_mixing_results_counts(module00_input14.get(), 6))
		module00_input15.bind("<KeyRelease>", lambda event: services.set_mixing_results_counts(module00_input15.get(), 7))
		module00_input16.bind("<KeyRelease>", lambda event: services.set_mixing_results_counts(module00_input16.get(), 8))
		module00_input17.bind("<KeyRelease>", lambda event: services.set_mixing_results_counts(module00_input17.get(), 9))

		module00_input18.bind("<KeyRelease>", lambda event: services.set_mixing_results_chance(module00_input18.get(), 1))
		module00_input19.bind("<KeyRelease>", lambda event: services.set_mixing_results_chance(module00_input19.get(), 2))
		module00_input20.bind("<KeyRelease>", lambda event: services.set_mixing_results_chance(module00_input20.get(), 3))
		module00_input21.bind("<KeyRelease>", lambda event: services.set_mixing_results_chance(module00_input21.get(), 4))
		module00_input22.bind("<KeyRelease>", lambda event: services.set_mixing_results_chance(module00_input22.get(), 5))
		module00_input23.bind("<KeyRelease>", lambda event: services.set_mixing_results_chance(module00_input23.get(), 6))
		module00_input24.bind("<KeyRelease>", lambda event: services.set_mixing_results_chance(module00_input24.get(), 7))
		module00_input25.bind("<KeyRelease>", lambda event: services.set_mixing_results_chance(module00_input25.get(), 8))
		module00_input26.bind("<KeyRelease>", lambda event: services.set_mixing_results_chance(module00_input26.get(), 9))


		#fluids
		module00_slot18=tk.Button(root,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.set_mixing_fluids(module00_slot18,"ins_fluid1"),highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color)
		module00_slot18.place(x=375,y=40)
		module00_slot19=tk.Button(root,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.set_mixing_fluids(module00_slot19,"ins_fluid2"),highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color)
		module00_slot19.place(x=375,y=95)
		module00_slot20=tk.Button(root,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.set_mixing_fluids(module00_slot20,"results_fluids1"),highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color)
		module00_slot20.place(x=790,y=40)
		module00_slot21=tk.Button(root,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.set_mixing_fluids(module00_slot21,"results_fluids2"),highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color)
		module00_slot21.place(x=790,y=95)


		module00_input27 = tk.Entry(root, width=7, validate="key", validatecommand=vcmd,
									background=light_bg_color, borderwidth=0, highlightthickness=1,
									highlightbackground=outline_collor, highlightcolor=outline_collor, 
									foreground=text_color)
		module00_input27.insert(0, 1)
		module00_input27.place(x=435, y=45)  # Nový widget

		module00_input28 = tk.Entry(root, width=7, validate="key", validatecommand=vcmd,
									background=light_bg_color, borderwidth=0, highlightthickness=1,
									highlightbackground=outline_collor, highlightcolor=outline_collor, 
									foreground=text_color)
		module00_input28.insert(0, 1)
		module00_input28.place(x=435, y=100)  # Nový widget

		module00_input29 = tk.Entry(root, width=7, validate="key", validatecommand=vcmd,
									background=light_bg_color, borderwidth=0, highlightthickness=1,
									highlightbackground=outline_collor, highlightcolor=outline_collor, 
									foreground=text_color)
		module00_input29.insert(0, 1)
		module00_input29.place(x=850, y=45)  # Nový widget

		module00_input30 = tk.Entry(root, width=7, validate="key", validatecommand=vcmd,
									background=light_bg_color, borderwidth=0, highlightthickness=1,
									highlightbackground=outline_collor, highlightcolor=outline_collor, 
									foreground=text_color)
		module00_input30.insert(0, 1)
		#module00_input30.place(x=915, y=45)  # Nový widget

		module00_input31 = tk.Entry(root, width=7, validate="key", validatecommand=vcmd,
									background=light_bg_color, borderwidth=0, highlightthickness=1,
									highlightbackground=outline_collor, highlightcolor=outline_collor, 
									foreground=text_color)
		module00_input31.place(x=850, y=100)
		module00_input31.insert(0,1)  # Nový widget

		module00_input32 = tk.Entry(root, width=7, validate="key", validatecommand=vcmd,
									background=light_bg_color, borderwidth=0, highlightthickness=1,
									highlightbackground=outline_collor, highlightcolor=outline_collor, 
									foreground=text_color)
		module00_input32.insert(0, 1)
		#module00_input32.place(x=915, y=100)  # Nový widget



		module00_input27.bind("<KeyRelease>", lambda event: services.set_fluids_parms(1,module00_input27.get()))
		module00_input28.bind("<KeyRelease>", lambda event: services.set_fluids_parms(2,module00_input28.get()))
		module00_input29.bind("<KeyRelease>", lambda event: services.set_fluids_parms(3,module00_input29.get()))
		module00_input30.bind("<KeyRelease>", lambda event: services.set_fluids_parms(4,module00_input30.get()))
		module00_input31.bind("<KeyRelease>", lambda event: services.set_fluids_parms(5,module00_input31.get()))
		module00_input32.bind("<KeyRelease>", lambda event: services.set_fluids_parms(6,module00_input32.get()))

		module00_select00 = ttk.Combobox(root,width=10,values=["none","heated","superheated"],state="readonly")
		module00_select00.place(x=500,y=44)
		module00_select00.bind("<<ComboboxSelected>>",lambda event:services.update_mixing_hate(str(module00_select00.get())))



		#labels
		label01 = tk.Label(root,text="Count",foreground=text_color,background=dark_bg_color,font=underlined_font0)
		label01.place(x=310,y=20)
		label02 = tk.Label(root,text="Count",foreground=text_color,background=dark_bg_color,font=underlined_font0)
		label02.place(x=660,y=20)
		label03 = tk.Label(root,text="Chance",foreground=text_color,background=dark_bg_color,font=underlined_font0)
		label03.place(x=725,y=20)

		label04 = tk.Label(root,text="Amaunt",foreground=text_color,background=dark_bg_color,font=underlined_font0)
		label04.place(x=435,y=20)
		label05 = tk.Label(root,text="Heat Level",foreground=text_color,background=dark_bg_color,font=underlined_font0)
		label05.place(x=500,y=20)
		label06 = tk.Label(root,text="Amaunt",foreground=text_color,background=dark_bg_color,font=underlined_font0)
		label06.place(x=850,y=20)
		label07 = tk.Label(root,text="Chance",foreground=text_color,background=dark_bg_color,font=underlined_font0)
		#label07.place(x=915,y=20)

		element_database = [
			module00_slot00, module00_slot01, module00_slot02, module00_slot03,
			module00_slot04, module00_slot05, module00_slot06, module00_slot07,
			module00_slot08, module00_slot09, module00_slot10, module00_slot11,
			module00_slot12, module00_slot13, module00_slot14, module00_slot15,
			module00_slot16, module00_slot17, module00_slot18, module00_slot19,
			module00_slot20, module00_slot21,module00_input00,module00_input01,
			module00_input02,module00_input03,module00_input04,module00_input05,
			module00_input06,module00_input07,module00_input08,module00_input09,
			module00_input10,module00_input11,module00_input12,module00_input13,
			module00_input14,module00_input15,module00_input16,module00_input17,
			module00_input18, module00_input19, module00_input20, module00_input21,
			module00_input22, module00_input23, module00_input24, module00_input25,
			module00_input26, module00_input27, module00_input28, module00_input29,
			module00_input30, module00_input31, module00_input32, module00_select00
			] + [label01,label02,label03,label04,label05,label06,label07]

	if modules == "create_item_application":

		module00_slot00=tk.Button(root,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_item_application_updates("in",module00_slot00),highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color)
		module00_slot00.place(x=449,y=193)

		module00_slot01=tk.Button(root,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_item_application_updates("sub_in",module00_slot01),highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color)
		module00_slot01.place(x=511,y=193)

		consument_value = tk.IntVar(root)

		block_checkbox1 = tk.Checkbutton(root,text="Consume Item",command=lambda:services.update_crafting_key("consument",str(consument_value.get())),variable=consument_value,onvalue=1,offvalue=0,background=light_bg_color,foreground=text_color,highlightbackground=outline_collor,highlightcolor=outline_collor,activebackground=light_bg_color,activeforeground=text_color,selectcolor=light_bg_color,width=13,anchor="w")
		block_checkbox1.place(x=438,y=258)
		

		add_button = tk.Button(root,background=light_bg_color,activebackground=outline_collor,foreground=text_color,activeforeground="#000000",highlightbackground=outline_collor,highlightcolor=outline_collor,highlightthickness=1,text="Add Item",width=46,command=lambda:services.add_result_pressing(update_pressing_result))
		add_button.place(y=454,x=583)


		main_frame = tk.Frame(root, background=dark_bg_color)
		main_frame.place(x=570,y=183)
		canvas = tk.Canvas(main_frame,background=light_bg_color,highlightbackground=outline_collor,highlightcolor=outline_collor)
		canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1, pady=(10, 10), padx=(10, 0))

		scrollbar = tk.Scrollbar(main_frame, orient=tk.VERTICAL, command=canvas.yview)
		scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=(10, 10), padx=(0, 10))

		canvas.configure(yscrollcommand=scrollbar.set)
		canvas.config(width=375)
		canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

		inner_frame = tk.Frame(canvas,background=light_bg_color)
		canvas.create_window((0, 0), window=inner_frame, anchor="nw")
		element_database = [module00_slot00,module00_slot01,main_frame,canvas,scrollbar,block_checkbox1,consument_value,add_button]
		def update_pressing_result(results,update_images = False):
			global element_database
			loop = 3
			element_database = [module00_slot00,module00_slot01,main_frame,canvas,scrollbar,block_checkbox1,consument_value,add_button]
			inputs_count = []
			inputs_chance = []
			input_slot = []
			remove_buttons_elements = []
			titles_elements = []
			for widget in inner_frame.winfo_children():
					widget.destroy()
			for result in results:
				loop = loop + 1
				element_frame = tk.Frame(inner_frame,background=light_bg_color,highlightbackground=outline_collor,highlightcolor=outline_collor,highlightthickness=1)
				element_frame.pack(fill=tk.X, pady=2,padx=(5,0))
				slot = tk.Button(element_frame,image=I_slot00,borderwidth=0,highlightthickness=1,highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color)
				slot.config(command=lambda cl = slot:services.set_result_pressing(cl))
				slot.pack(side=tk.LEFT,padx=(2,2),pady=(2,2))
				slot.result = result
				title00 = tk.Label(element_frame,text="count",width=5,background=light_bg_color,foreground=text_color)
				title00.pack(side=tk.LEFT,padx=(2,0),pady=(2,2))
				text00=tk.Entry(element_frame,width=3,validate="key",validatecommand=(vcmd,"%P"),background=light_bg_color,borderwidth=0,highlightthickness=1,highlightbackground=outline_collor,highlightcolor=outline_collor,foreground=text_color)
				text00.pack(side=tk.LEFT,padx=(1,2),pady=(2,2))
				text00.insert(0,result.get("count"))
				text00.bind("<KeyRelease>", lambda event, vl = text00, cl = slot:services.set_result_pressing_count(vl,cl))
				title02 = tk.Label(element_frame,text="chance",width=6,background=light_bg_color,foreground=text_color)
				title02.pack(side=tk.LEFT,padx=(2,0),pady=(2,2))
				text01=tk.Entry(element_frame,width=3,validate="key",validatecommand=(vcmd,"%P"),background=light_bg_color,borderwidth=0,highlightthickness=1,highlightbackground=outline_collor,highlightcolor=outline_collor,foreground=text_color)
				text01.pack(side=tk.LEFT,padx=(1,2),pady=(2,2))
				text01.insert(0,result.get("chance"))
				text01.bind("<KeyRelease>", lambda event, vl = text01, cl = slot:services.set_result_pressing_chance(vl,cl))
				title03 = tk.Label(element_frame,text="%",width=1,background=light_bg_color,foreground=text_color)
				title03.pack(side=tk.LEFT,padx=(0,2),pady=(2,2))
				remove_button = tk.Button(element_frame,background=light_bg_color,activebackground=outline_collor,foreground=text_color,activeforeground="#000000",highlightbackground=outline_collor,highlightcolor=outline_collor,highlightthickness=1,text="Remove",width=6,command = lambda vl = slot:services.remove_result_pressing(vl,update=update_pressing_result))
				remove_button.pack(side=tk.LEFT,padx=(50,2),pady=(2,2))
				remove_buttons_elements.append(remove_button)
				titles_elements.append(title00)
				titles_elements.append(title02)
				titles_elements.append(title03)
				inputs_chance.append(text01)
				inputs_count.append(text00)
				element_database.append(slot)
				input_slot.append(slot)
			if update_images == True:
				services.update_pressing_slot_images(input_slot)
			element_database = element_database + inputs_count + inputs_chance + remove_buttons_elements + [add_button] + titles_elements
			inner_frame.update_idletasks()
			inner_frame.update()
			canvas.configure(scrollregion=canvas.bbox("all"))
		update_pressing_result(results)

	if modules == "create_deployng":

		module00_slot00=tk.Button(root,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_item_application_updates("in",module00_slot00),highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color)
		module00_slot00.place(x=449,y=193)

		module00_slot01=tk.Button(root,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_item_application_updates("sub_in",module00_slot01),highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color)
		module00_slot01.place(x=511,y=193)

		consument_value = tk.IntVar(root)

		block_checkbox1 = tk.Checkbutton(root,text="Consume Item",command=lambda:services.update_crafting_key("consument",str(consument_value.get())),variable=consument_value,onvalue=1,offvalue=0,background=light_bg_color,foreground=text_color,highlightbackground=outline_collor,highlightcolor=outline_collor,activebackground=light_bg_color,activeforeground=text_color,selectcolor=light_bg_color,width=13,anchor="w")
		block_checkbox1.place(x=438,y=258)
		

		add_button = tk.Button(root,background=light_bg_color,activebackground=outline_collor,foreground=text_color,activeforeground="#000000",highlightbackground=outline_collor,highlightcolor=outline_collor,highlightthickness=1,text="Add Item",width=46,command=lambda:services.add_result_pressing(update_pressing_result))
		add_button.place(y=454,x=583)


		main_frame = tk.Frame(root, background=dark_bg_color)
		main_frame.place(x=570,y=183)
		canvas = tk.Canvas(main_frame,background=light_bg_color,highlightbackground=outline_collor,highlightcolor=outline_collor)
		canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1, pady=(10, 10), padx=(10, 0))

		scrollbar = tk.Scrollbar(main_frame, orient=tk.VERTICAL, command=canvas.yview)
		scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=(10, 10), padx=(0, 10))

		canvas.configure(yscrollcommand=scrollbar.set)
		canvas.config(width=375)
		canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

		inner_frame = tk.Frame(canvas,background=light_bg_color)
		canvas.create_window((0, 0), window=inner_frame, anchor="nw")
		element_database = [module00_slot00,module00_slot01,main_frame,canvas,scrollbar,block_checkbox1,consument_value,add_button]
		def update_pressing_result(results,update_images = False):
			global element_database
			loop = 3
			element_database = [module00_slot00,module00_slot01,main_frame,canvas,scrollbar,block_checkbox1,consument_value,add_button]
			inputs_count = []
			inputs_chance = []
			input_slot = []
			remove_buttons_elements = []
			titles_elements = []
			for widget in inner_frame.winfo_children():
					widget.destroy()
			for result in results:
				loop = loop + 1
				element_frame = tk.Frame(inner_frame,background=light_bg_color,highlightbackground=outline_collor,highlightcolor=outline_collor,highlightthickness=1)
				element_frame.pack(fill=tk.X, pady=2,padx=(5,0))
				slot = tk.Button(element_frame,image=I_slot00,borderwidth=0,highlightthickness=1,highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color)
				slot.config(command=lambda cl = slot:services.set_result_pressing(cl))
				slot.pack(side=tk.LEFT,padx=(2,2),pady=(2,2))
				slot.result = result
				title00 = tk.Label(element_frame,text="count",width=5,background=light_bg_color,foreground=text_color)
				title00.pack(side=tk.LEFT,padx=(2,0),pady=(2,2))
				text00=tk.Entry(element_frame,width=3,validate="key",validatecommand=(vcmd,"%P"),background=light_bg_color,borderwidth=0,highlightthickness=1,highlightbackground=outline_collor,highlightcolor=outline_collor,foreground=text_color)
				text00.pack(side=tk.LEFT,padx=(1,2),pady=(2,2))
				text00.insert(0,result.get("count"))
				text00.bind("<KeyRelease>", lambda event, vl = text00, cl = slot:services.set_result_pressing_count(vl,cl))
				title02 = tk.Label(element_frame,text="chance",width=6,background=light_bg_color,foreground=text_color)
				title02.pack(side=tk.LEFT,padx=(2,0),pady=(2,2))
				text01=tk.Entry(element_frame,width=3,validate="key",validatecommand=(vcmd,"%P"),background=light_bg_color,borderwidth=0,highlightthickness=1,highlightbackground=outline_collor,highlightcolor=outline_collor,foreground=text_color)
				text01.pack(side=tk.LEFT,padx=(1,2),pady=(2,2))
				text01.insert(0,result.get("chance"))
				text01.bind("<KeyRelease>", lambda event, vl = text01, cl = slot:services.set_result_pressing_chance(vl,cl))
				title03 = tk.Label(element_frame,text="%",width=1,background=light_bg_color,foreground=text_color)
				title03.pack(side=tk.LEFT,padx=(0,2),pady=(2,2))
				remove_button = tk.Button(element_frame,background=light_bg_color,activebackground=outline_collor,foreground=text_color,activeforeground="#000000",highlightbackground=outline_collor,highlightcolor=outline_collor,highlightthickness=1,text="Remove",width=6,command = lambda vl = slot:services.remove_result_pressing(vl,update=update_pressing_result))
				remove_button.pack(side=tk.LEFT,padx=(50,2),pady=(2,2))
				remove_buttons_elements.append(remove_button)
				titles_elements.append(title00)
				titles_elements.append(title02)
				titles_elements.append(title03)
				inputs_chance.append(text01)
				inputs_count.append(text00)
				element_database.append(slot)
				input_slot.append(slot)
			if update_images == True:
				services.update_pressing_slot_images(input_slot)
			element_database = element_database + inputs_count + inputs_chance + remove_buttons_elements + [add_button] + titles_elements
			inner_frame.update_idletasks()
			inner_frame.update()
			canvas.configure(scrollregion=canvas.bbox("all"))
		update_pressing_result(results)		

	if modules == "create_crushing":
		module03_slot00 = tk.Button(root,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module03_slot00,"in"),highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color)
		module03_slot00.place(y=179,x=446)
		add_button = tk.Button(root,background=light_bg_color,activebackground=outline_collor,foreground=text_color,activeforeground="#000000",highlightbackground=outline_collor,highlightcolor=outline_collor,highlightthickness=1,text="Add Item",width=46,command=lambda:services.add_result_pressing(update_pressing_result))
		add_button.place(y=454,x=583)

		module03_arrow00=tk.Button(root,image=I_arrow00,width=59,borderwidth=0,highlightthickness=0,background=dark_bg_color,activebackground=dark_bg_color)
		module03_arrow00.place(x=511,y=175)
		main_frame = tk.Frame(root, background=dark_bg_color)
		main_frame.place(x=572,y=163)

		time_input=tk.Entry(root,width=5,background=light_bg_color,borderwidth=0,highlightthickness=1,highlightbackground=outline_collor,highlightcolor=outline_collor,foreground=text_color)
		time_input.place(x=510,y=245)
		time_input.bind("<KeyRelease>", lambda event:services.update_crafting_key("time",int(time_input.get())))

		time_label = tk.Label(root,text="Process Time (Sec)",width=18,background=light_bg_color,foreground=text_color)
		time_label.place(x=355,y=245)

		canvas = tk.Canvas(main_frame,background=light_bg_color,highlightbackground=outline_collor,highlightcolor=outline_collor)
		canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1, pady=(10, 10), padx=(10, 0))

		scrollbar = tk.Scrollbar(main_frame, orient=tk.VERTICAL, command=canvas.yview)
		scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=(10, 10), padx=(0, 10))

		canvas.configure(yscrollcommand=scrollbar.set)
		canvas.config(width=375)

		canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

		inner_frame = tk.Frame(canvas,background=light_bg_color)
		canvas.create_window((0, 0), window=inner_frame, anchor="nw")
		element_database = [module03_slot00,main_frame,canvas,scrollbar,add_button,time_input,time_label]
		def update_pressing_result(results,update_images = False):
			global element_database
			loop = 3
			element_database = [module03_slot00,main_frame,canvas,scrollbar,add_button,time_input,time_label]
			inputs_count = []
			inputs_chance = []
			input_slot = []
			remove_buttons_elements = []
			titles_elements = []
			for widget in inner_frame.winfo_children():
					widget.destroy()
			for result in results:
				loop = loop + 1
				element_frame = tk.Frame(inner_frame,background=light_bg_color,highlightbackground=outline_collor,highlightcolor=outline_collor,highlightthickness=1)
				element_frame.pack(fill=tk.X, pady=2,padx=(5,0))
				slot = tk.Button(element_frame,image=I_slot00,borderwidth=0,highlightthickness=1,highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color)
				slot.config(command=lambda cl = slot:services.set_result_pressing(cl))
				slot.pack(side=tk.LEFT,padx=(2,2),pady=(2,2))
				slot.result = result
				title00 = tk.Label(element_frame,text="count",width=5,background=light_bg_color,foreground=text_color)
				title00.pack(side=tk.LEFT,padx=(2,0),pady=(2,2))
				text00=tk.Entry(element_frame,width=3,validate="key",validatecommand=(vcmd,"%P"),background=light_bg_color,borderwidth=0,highlightthickness=1,highlightbackground=outline_collor,highlightcolor=outline_collor,foreground=text_color)
				text00.pack(side=tk.LEFT,padx=(1,2),pady=(2,2))
				text00.insert(0,result.get("count"))
				text00.bind("<KeyRelease>", lambda event, vl = text00, cl = slot:services.set_result_pressing_count(vl,cl))
				title02 = tk.Label(element_frame,text="chance",width=6,background=light_bg_color,foreground=text_color)
				title02.pack(side=tk.LEFT,padx=(2,0),pady=(2,2))
				text01=tk.Entry(element_frame,width=3,validate="key",validatecommand=(vcmd,"%P"),background=light_bg_color,borderwidth=0,highlightthickness=1,highlightbackground=outline_collor,highlightcolor=outline_collor,foreground=text_color)
				text01.pack(side=tk.LEFT,padx=(1,2),pady=(2,2))
				text01.insert(0,result.get("chance"))
				text01.bind("<KeyRelease>", lambda event, vl = text01, cl = slot:services.set_result_pressing_chance(vl,cl))
				title03 = tk.Label(element_frame,text="%",width=1,background=light_bg_color,foreground=text_color)
				title03.pack(side=tk.LEFT,padx=(0,2),pady=(2,2))
				remove_button = tk.Button(element_frame,background=light_bg_color,activebackground=outline_collor,foreground=text_color,activeforeground="#000000",highlightbackground=outline_collor,highlightcolor=outline_collor,highlightthickness=1,text="Remove",width=6,command = lambda vl = slot:services.remove_result_pressing(vl,update=update_pressing_result))
				remove_button.pack(side=tk.LEFT,padx=(50,2),pady=(2,2))
				remove_buttons_elements.append(remove_button)
				titles_elements.append(title00)
				titles_elements.append(title02)
				titles_elements.append(title03)
				inputs_chance.append(text01)
				inputs_count.append(text00)
				element_database.append(slot)
				input_slot.append(slot)
			if update_images == True:
				services.update_pressing_slot_images(input_slot)
			element_database = element_database + inputs_count + inputs_chance + remove_buttons_elements + [add_button,module03_arrow00] + titles_elements
			inner_frame.update_idletasks()
			canvas.configure(scrollregion=canvas.bbox("all"))
		update_pressing_result(results)

	if modules == "create_milling":
		module03_slot00 = tk.Button(root,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module03_slot00,"in"),highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color)
		module03_slot00.place(y=179,x=446)
		add_button = tk.Button(root,background=light_bg_color,activebackground=outline_collor,foreground=text_color,activeforeground="#000000",highlightbackground=outline_collor,highlightcolor=outline_collor,highlightthickness=1,text="Add Item",width=46,command=lambda:services.add_result_pressing(update_pressing_result))
		add_button.place(y=454,x=583)


		module03_arrow00=tk.Button(root,image=I_arrow00,width=59,borderwidth=0,highlightthickness=0,background=dark_bg_color,activebackground=dark_bg_color)
		module03_arrow00.place(x=511,y=175)
		main_frame = tk.Frame(root, background=dark_bg_color)
		main_frame.place(x=572,y=163)

		time_input=tk.Entry(root,width=5,background=light_bg_color,borderwidth=0,highlightthickness=1,highlightbackground=outline_collor,highlightcolor=outline_collor,foreground=text_color)
		time_input.place(x=510,y=245)
		time_input.bind("<KeyRelease>", lambda event:services.update_crafting_key("time",int(time_input.get())))

		time_label = tk.Label(root,text="Process Time (Sec)",width=18,background=light_bg_color,foreground=text_color)
		time_label.place(x=355,y=245)

		canvas = tk.Canvas(main_frame,background=light_bg_color,highlightbackground=outline_collor,highlightcolor=outline_collor)
		canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1, pady=(10, 10), padx=(10, 0))

		scrollbar = tk.Scrollbar(main_frame, orient=tk.VERTICAL, command=canvas.yview)
		scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=(10, 10), padx=(0, 10))

		canvas.configure(yscrollcommand=scrollbar.set)
		canvas.config(width=375)

		canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

		inner_frame = tk.Frame(canvas,background=light_bg_color)
		canvas.create_window((0, 0), window=inner_frame, anchor="nw")
		element_database = [module03_slot00,main_frame,canvas,scrollbar,add_button,time_input,time_label]
		def update_pressing_result(results,update_images = False):
			global element_database
			loop = 3
			element_database = [module03_slot00,main_frame,canvas,scrollbar,add_button,time_input,time_label]
			inputs_count = []
			inputs_chance = []
			input_slot = []
			remove_buttons_elements = []
			titles_elements = []
			for widget in inner_frame.winfo_children():
					widget.destroy()
			for result in results:
				loop = loop + 1
				element_frame = tk.Frame(inner_frame,background=light_bg_color,highlightbackground=outline_collor,highlightcolor=outline_collor,highlightthickness=1)
				element_frame.pack(fill=tk.X, pady=2,padx=(5,0))
				slot = tk.Button(element_frame,image=I_slot00,borderwidth=0,highlightthickness=1,highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color)
				slot.config(command=lambda cl = slot:services.set_result_pressing(cl))
				slot.pack(side=tk.LEFT,padx=(2,2),pady=(2,2))
				slot.result = result
				title00 = tk.Label(element_frame,text="count",width=5,background=light_bg_color,foreground=text_color)
				title00.pack(side=tk.LEFT,padx=(2,0),pady=(2,2))
				text00=tk.Entry(element_frame,width=3,validate="key",validatecommand=(vcmd,"%P"),background=light_bg_color,borderwidth=0,highlightthickness=1,highlightbackground=outline_collor,highlightcolor=outline_collor,foreground=text_color)
				text00.pack(side=tk.LEFT,padx=(1,2),pady=(2,2))
				text00.insert(0,result.get("count"))
				text00.bind("<KeyRelease>", lambda event, vl = text00, cl = slot:services.set_result_pressing_count(vl,cl))
				title02 = tk.Label(element_frame,text="chance",width=6,background=light_bg_color,foreground=text_color)
				title02.pack(side=tk.LEFT,padx=(2,0),pady=(2,2))
				text01=tk.Entry(element_frame,width=3,validate="key",validatecommand=(vcmd,"%P"),background=light_bg_color,borderwidth=0,highlightthickness=1,highlightbackground=outline_collor,highlightcolor=outline_collor,foreground=text_color)
				text01.pack(side=tk.LEFT,padx=(1,2),pady=(2,2))
				text01.insert(0,result.get("chance"))
				text01.bind("<KeyRelease>", lambda event, vl = text01, cl = slot:services.set_result_pressing_chance(vl,cl))
				title03 = tk.Label(element_frame,text="%",width=1,background=light_bg_color,foreground=text_color)
				title03.pack(side=tk.LEFT,padx=(0,2),pady=(2,2))
				remove_button = tk.Button(element_frame,background=light_bg_color,activebackground=outline_collor,foreground=text_color,activeforeground="#000000",highlightbackground=outline_collor,highlightcolor=outline_collor,highlightthickness=1,text="Remove",width=6,command = lambda vl = slot:services.remove_result_pressing(vl,update=update_pressing_result))
				remove_button.pack(side=tk.LEFT,padx=(50,2),pady=(2,2))
				remove_buttons_elements.append(remove_button)
				titles_elements.append(title00)
				titles_elements.append(title02)
				titles_elements.append(title03)
				inputs_chance.append(text01)
				inputs_count.append(text00)
				element_database.append(slot)
				input_slot.append(slot)
			if update_images == True:
				services.update_pressing_slot_images(input_slot)
			element_database = element_database + inputs_count + inputs_chance + remove_buttons_elements + [add_button,module03_arrow00] + titles_elements
			inner_frame.update_idletasks()
			canvas.configure(scrollregion=canvas.bbox("all"))
		update_pressing_result(results)

	if modules == "create_cutting":
		module03_slot00 = tk.Button(root,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module03_slot00,"in"),highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color)
		module03_slot00.place(y=179,x=446)
		add_button = tk.Button(root,background=light_bg_color,activebackground=outline_collor,foreground=text_color,activeforeground="#000000",highlightbackground=outline_collor,highlightcolor=outline_collor,highlightthickness=1,text="Add Item",width=46,command=lambda:services.add_result_pressing(update_pressing_result))
		add_button.place(y=454,x=583)

		module03_arrow00=tk.Button(root,image=I_arrow00,width=59,borderwidth=0,highlightthickness=0,background=dark_bg_color,activebackground=dark_bg_color)
		module03_arrow00.place(x=511,y=175)
		main_frame = tk.Frame(root, background=dark_bg_color)
		main_frame.place(x=572,y=163)

		time_input=tk.Entry(root,width=5,background=light_bg_color,borderwidth=0,highlightthickness=1,highlightbackground=outline_collor,highlightcolor=outline_collor,foreground=text_color)
		time_input.place(x=510,y=245)
		time_input.bind("<KeyRelease>", lambda event:services.update_crafting_key("time",int(time_input.get())))

		time_label = tk.Label(root,text="Process Time (Sec)",width=18,background=light_bg_color,foreground=text_color)
		time_label.place(x=355,y=245)

		canvas = tk.Canvas(main_frame,background=light_bg_color,highlightbackground=outline_collor,highlightcolor=outline_collor)
		canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1, pady=(10, 10), padx=(10, 0))

		scrollbar = tk.Scrollbar(main_frame, orient=tk.VERTICAL, command=canvas.yview)
		scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=(10, 10), padx=(0, 10))

		canvas.configure(yscrollcommand=scrollbar.set)
		canvas.config(width=375)

		canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

		inner_frame = tk.Frame(canvas,background=light_bg_color)
		canvas.create_window((0, 0), window=inner_frame, anchor="nw")
		element_database = [module03_slot00,main_frame,canvas,scrollbar,add_button,time_input,time_label]
		def update_pressing_result(results,update_images = False):
			global element_database
			loop = 3
			element_database = [module03_slot00,main_frame,canvas,scrollbar,add_button,time_input,time_label]
			inputs_count = []
			inputs_chance = []
			input_slot = []
			remove_buttons_elements = []
			titles_elements = []
			for widget in inner_frame.winfo_children():
					widget.destroy()
			for result in results:
				loop = loop + 1
				element_frame = tk.Frame(inner_frame,background=light_bg_color,highlightbackground=outline_collor,highlightcolor=outline_collor,highlightthickness=1)
				element_frame.pack(fill=tk.X, pady=2,padx=(5,0))
				slot = tk.Button(element_frame,image=I_slot00,borderwidth=0,highlightthickness=1,highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color)
				slot.config(command=lambda cl = slot:services.set_result_pressing(cl))
				slot.pack(side=tk.LEFT,padx=(2,2),pady=(2,2))
				slot.result = result
				title00 = tk.Label(element_frame,text="count",width=5,background=light_bg_color,foreground=text_color)
				title00.pack(side=tk.LEFT,padx=(2,0),pady=(2,2))
				text00=tk.Entry(element_frame,width=3,validate="key",validatecommand=(vcmd,"%P"),background=light_bg_color,borderwidth=0,highlightthickness=1,highlightbackground=outline_collor,highlightcolor=outline_collor,foreground=text_color)
				text00.pack(side=tk.LEFT,padx=(1,2),pady=(2,2))
				text00.insert(0,result.get("count"))
				text00.bind("<KeyRelease>", lambda event, vl = text00, cl = slot:services.set_result_pressing_count(vl,cl))
				title02 = tk.Label(element_frame,text="chance",width=6,background=light_bg_color,foreground=text_color)
				title02.pack(side=tk.LEFT,padx=(2,0),pady=(2,2))
				text01=tk.Entry(element_frame,width=3,validate="key",validatecommand=(vcmd,"%P"),background=light_bg_color,borderwidth=0,highlightthickness=1,highlightbackground=outline_collor,highlightcolor=outline_collor,foreground=text_color)
				text01.pack(side=tk.LEFT,padx=(1,2),pady=(2,2))
				text01.insert(0,result.get("chance"))
				text01.bind("<KeyRelease>", lambda event, vl = text01, cl = slot:services.set_result_pressing_chance(vl,cl))
				title03 = tk.Label(element_frame,text="%",width=1,background=light_bg_color,foreground=text_color)
				title03.pack(side=tk.LEFT,padx=(0,2),pady=(2,2))
				remove_button = tk.Button(element_frame,background=light_bg_color,activebackground=outline_collor,foreground=text_color,activeforeground="#000000",highlightbackground=outline_collor,highlightcolor=outline_collor,highlightthickness=1,text="Remove",width=6,command = lambda vl = slot:services.remove_result_pressing(vl,update=update_pressing_result))
				remove_button.pack(side=tk.LEFT,padx=(50,2),pady=(2,2))
				remove_buttons_elements.append(remove_button)
				titles_elements.append(title00)
				titles_elements.append(title02)
				titles_elements.append(title03)
				inputs_chance.append(text01)
				inputs_count.append(text00)
				element_database.append(slot)
				input_slot.append(slot)
			if update_images == True:
				services.update_pressing_slot_images(input_slot)
			element_database = element_database + inputs_count + inputs_chance + remove_buttons_elements + [add_button,module03_arrow00] + titles_elements
			inner_frame.update_idletasks()
			canvas.configure(scrollregion=canvas.bbox("all"))
		update_pressing_result(results)

	if modules == "Vortex":
		frame = tk.Frame(root, bg=dark_bg_color,width=700,height=600)
		frame.place(x=206,y=3)

		# Textový widget s nastavením pozadí a popředí
		master = tkcode.CodeEditor(frame,language="javascript",autofocus=True,autoseparators=True,maxundo=100)
		master.pack(expand = True,fill=tk.BOTH)
		
		master.focus_set()
		def highlight_json_syntax(event=None):
			master.update_highlighter("mariana")
			text_content = master.get("1.0", tk.END)
			services.update_vortex(text_content)
		
		def set_focus(event=None):
			master.focus_set()
		root.bind("<Button-1>", set_focus)
		master.bind("<KeyRelease>", highlight_json_syntax)
		element_database = [master,frame]

	if modules == "Sequence Assembly":
		add_button = tk.Button(root,background=light_bg_color,activebackground=outline_collor,foreground=text_color,activeforeground="#000000",highlightbackground=outline_collor,highlightcolor=outline_collor,highlightthickness=1,text="Add Item",width=46,command=lambda:services.add_result_pressing(update_pressing_result))
		add_button.place(y=529,x=209)
		arsenal_menu = tk.Listbox(root,width=21,height=27,foreground=text_color,background=dark_bg_color,highlightthickness=1,highlightcolor=outline_collor,highlightbackground=outline_collor)
		arsenal_menu.place(x=819,y=9)
		for i in ["pressing","cutting","deployng","spouting"]:
			arsenal_menu.insert(tk.END,i)
		arsenal_menu.bind("<Button-3>",lambda event: services.arsenal_add(arsenal_menu,usage_arsenal_menu))
		#ins
		parm_frame = tk.Frame(root,background=dark_bg_color,width=417,height=163,highlightbackground=outline_collor,highlightcolor=outline_collor,highlightthickness=1)
		parm_frame.place(x=204,y=9)
		
		usage_arsenal_menu = tk.Listbox(root,width=21,height=27,foreground=text_color,background=dark_bg_color,highlightthickness=1,highlightcolor=outline_collor,highlightbackground=outline_collor)
		usage_arsenal_menu.place(x=629,y=9)
		
		parm_editor = tk.Text(parm_frame,background=dark_bg_color,foreground=text_color,width=50,height=8)
		parm_editor.place(x=5,y=10)
		parm_editor.bind("<KeyRelease>",lambda event:services.update_parms(usage_arsenal_menu,parm_editor.get("1.0",tk.END)))
		
		usage_arsenal_menu.bind("<<ListboxSelect>>",lambda event: services.update_parm_frame(parm_editor,usage_arsenal_menu,parm_frame))
		usage_arsenal_menu.bind("<Button-3>",lambda event: services.arsenal_remove(usage_arsenal_menu))

		up = ctk.CTkButton(root,width=50,text=f"\U000025B2",command=lambda: services.sequence_as_move_up(usage_arsenal_menu))
		up.place(x=560,y=175)
		down = ctk.CTkButton(root,width=50,text=f"\U000025BC",command=lambda: services.sequence_as_move_down(usage_arsenal_menu))
		down.place(x=560,y=205)
		loop_input=tk.Entry(root,width=5,background=light_bg_color,borderwidth=0,highlightthickness=1,highlightbackground=outline_collor,highlightcolor=outline_collor,foreground=text_color)
		loop_input.place(x=505,y=213)
		loop_input.bind("<KeyRelease>", lambda event:services.update_crafting_key("loops",int(loop_input.get())))
		loop_label = caption(root,text="Loops:",width=6)
		loop_label.place(x=455,y=213)
		caption(root,text="Input:").place(y=213,x=215)
		module03_slot00 = tk.Button(root,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module03_slot00,"in"),highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color)
		module03_slot00.place(y=178,x=250+7)
		caption(root,text="TransItem:").place(y=213,x=317)

		module03_slot01 = tk.Button(root,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module03_slot01,"transitionalItem"),highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color)
		module03_slot01.place(y=178,x=385+10)
		# results
		#open the box befotre eating pizza
		main_frame = tk.Frame(root, background=dark_bg_color)
		main_frame.place(x=201,y=237)
		
		canvas = tk.Canvas(main_frame,background=light_bg_color,highlightbackground=outline_collor,highlightcolor=outline_collor)
		canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1, pady=(10, 10), padx=(10, 0))

		scrollbar = tk.Scrollbar(main_frame, orient=tk.VERTICAL, command=canvas.yview)
		scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=(10, 10), padx=(0, 10))

		canvas.configure(yscrollcommand=scrollbar.set)
		canvas.config(width=375)

		canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

		inner_frame = tk.Frame(canvas,background=light_bg_color)
		canvas.create_window((0, 0), window=inner_frame, anchor="nw")
		# element database
		element_database = [module03_slot00,module03_slot01,loop_input,loop_label,usage_arsenal_menu,arsenal_menu,main_frame,canvas,scrollbar,add_button,parm_frame,parm_editor,up,down]
		def update_pressing_result(results,update_images = False):
			global element_database
			loop = 3
			element_database = [module03_slot00,module03_slot01,loop_input,loop_label,usage_arsenal_menu,arsenal_menu,main_frame,canvas,scrollbar,add_button,parm_frame,parm_editor,up,down]
			inputs_count = []
			inputs_chance = []
			input_slot = []
			remove_buttons_elements = []
			titles_elements = []
			for widget in inner_frame.winfo_children():
					widget.destroy()
			for result in results:
				loop = loop + 1
				element_frame = tk.Frame(inner_frame,background=light_bg_color,highlightbackground=outline_collor,highlightcolor=outline_collor,highlightthickness=1)
				element_frame.pack(fill=tk.X, pady=2,padx=(5,0))
				slot = tk.Button(element_frame,image=I_slot00,borderwidth=0,highlightthickness=1,highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color)
				slot.config(command=lambda cl = slot:services.set_result_pressing(cl))
				slot.pack(side=tk.LEFT,padx=(2,2),pady=(2,2))
				slot.result = result
				title00 = tk.Label(element_frame,text="count",width=5,background=light_bg_color,foreground=text_color)
				title00.pack(side=tk.LEFT,padx=(2,0),pady=(2,2))
				text00=tk.Entry(element_frame,width=3,validate="key",validatecommand=(vcmd,"%P"),background=light_bg_color,borderwidth=0,highlightthickness=1,highlightbackground=outline_collor,highlightcolor=outline_collor,foreground=text_color)
				text00.pack(side=tk.LEFT,padx=(1,2),pady=(2,2))
				text00.insert(0,result.get("count"))
				text00.bind("<KeyRelease>", lambda event, vl = text00, cl = slot:services.set_result_pressing_count(vl,cl))
				title02 = tk.Label(element_frame,text="chance",width=6,background=light_bg_color,foreground=text_color)
				title02.pack(side=tk.LEFT,padx=(2,0),pady=(2,2))
				text01=tk.Entry(element_frame,width=3,validate="key",validatecommand=(vcmd,"%P"),background=light_bg_color,borderwidth=0,highlightthickness=1,highlightbackground=outline_collor,highlightcolor=outline_collor,foreground=text_color)
				text01.pack(side=tk.LEFT,padx=(1,2),pady=(2,2))
				text01.insert(0,result.get("chance"))
				text01.bind("<KeyRelease>", lambda event, vl = text01, cl = slot:services.set_result_pressing_chance(vl,cl))
				title03 = tk.Label(element_frame,text="%",width=1,background=light_bg_color,foreground=text_color)
				title03.pack(side=tk.LEFT,padx=(0,2),pady=(2,2))
				remove_button = tk.Button(element_frame,background=light_bg_color,activebackground=outline_collor,foreground=text_color,activeforeground="#000000",highlightbackground=outline_collor,highlightcolor=outline_collor,highlightthickness=1,text="Remove",width=6,command = lambda vl = slot:services.remove_result_pressing(vl,update=update_pressing_result))
				remove_button.pack(side=tk.LEFT,padx=(50,2),pady=(2,2))
				remove_buttons_elements.append(remove_button)
				titles_elements.append(title00)
				titles_elements.append(title02)
				titles_elements.append(title03)
				inputs_chance.append(text01)
				inputs_count.append(text00)
				element_database.append(slot)
				input_slot.append(slot)
			if update_images == True:
				services.update_pressing_slot_images(input_slot)
			element_database = element_database + inputs_count + inputs_chance + remove_buttons_elements + [add_button] + titles_elements
			inner_frame.update_idletasks()
			canvas.configure(scrollregion=canvas.bbox("all"))
		update_pressing_result(results)	

	if modules == "create_spouting":
		module03_slot00 = tk.Button(root,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module03_slot00,"in"),highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color)
		module03_slot00.place(y=179,x=446)
		module03_slot01 = tk.Button(root,image=I_slot00,borderwidth=0,highlightthickness=1,command=lambda:services.create_crafting(module03_slot01,"subin"),highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color)
		module03_slot01.place(y=179,x=385)
		add_button = tk.Button(root,background=light_bg_color,activebackground=outline_collor,foreground=text_color,activeforeground="#000000",highlightbackground=outline_collor,highlightcolor=outline_collor,highlightthickness=1,text="Add Item",width=46,command=lambda:services.add_result_pressing(update_pressing_result))
		add_button.place(y=454,x=583)

		module03_arrow00=tk.Button(root,image=I_arrow00,width=59,borderwidth=0,highlightthickness=0,background=dark_bg_color,activebackground=dark_bg_color)
		module03_arrow00.place(x=511,y=175)
		main_frame = tk.Frame(root, background=dark_bg_color)
		main_frame.place(x=572,y=163)

		time_input=tk.Entry(root,width=5,background=light_bg_color,borderwidth=0,highlightthickness=1,highlightbackground=outline_collor,highlightcolor=outline_collor,foreground=text_color)
		time_input.place(x=460,y=238)
		time_input.bind("<KeyRelease>", lambda event:services.update_crafting_key("amount",int(time_input.get())))
		
		time_label = tk.Label(root,text="Amount",width=7,background=light_bg_color,foreground=text_color)
		time_label.place(x=398,y=239)
		canvas = tk.Canvas(main_frame,background=light_bg_color,highlightbackground=outline_collor,highlightcolor=outline_collor)
		canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1, pady=(10, 10), padx=(10, 0))

		scrollbar = tk.Scrollbar(main_frame, orient=tk.VERTICAL, command=canvas.yview)
		scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=(10, 10), padx=(0, 10))

		canvas.configure(yscrollcommand=scrollbar.set)
		canvas.config(width=375)

		canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

		inner_frame = tk.Frame(canvas,background=light_bg_color)
		canvas.create_window((0, 0), window=inner_frame, anchor="nw")
		element_database = [module03_slot00,main_frame,canvas,scrollbar,add_button,time_input,time_label,module03_slot01]
		def update_pressing_result(results,update_images = False):
			global element_database
			loop = 3
			element_database = [module03_slot00,main_frame,canvas,scrollbar,add_button,time_input,time_label,module03_slot01]
			inputs_count = []
			inputs_chance = []
			input_slot = []
			remove_buttons_elements = []
			titles_elements = []
			for widget in inner_frame.winfo_children():
					widget.destroy()
			for result in results:
				loop = loop + 1
				element_frame = tk.Frame(inner_frame,background=light_bg_color,highlightbackground=outline_collor,highlightcolor=outline_collor,highlightthickness=1)
				element_frame.pack(fill=tk.X, pady=2,padx=(5,0))
				slot = tk.Button(element_frame,image=I_slot00,borderwidth=0,highlightthickness=1,highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color)
				slot.config(command=lambda cl = slot:services.set_result_pressing(cl))
				slot.pack(side=tk.LEFT,padx=(2,2),pady=(2,2))
				slot.result = result
				title00 = tk.Label(element_frame,text="count",width=5,background=light_bg_color,foreground=text_color)
				title00.pack(side=tk.LEFT,padx=(2,0),pady=(2,2))
				text00=tk.Entry(element_frame,width=3,validate="key",validatecommand=(vcmd,"%P"),background=light_bg_color,borderwidth=0,highlightthickness=1,highlightbackground=outline_collor,highlightcolor=outline_collor,foreground=text_color)
				text00.pack(side=tk.LEFT,padx=(1,2),pady=(2,2))
				text00.insert(0,result.get("count"))
				text00.bind("<KeyRelease>", lambda event, vl = text00, cl = slot:services.set_result_pressing_count(vl,cl))
				title02 = tk.Label(element_frame,text="chance",width=6,background=light_bg_color,foreground=text_color)
				title02.pack(side=tk.LEFT,padx=(2,0),pady=(2,2))
				text01=tk.Entry(element_frame,width=3,validate="key",validatecommand=(vcmd,"%P"),background=light_bg_color,borderwidth=0,highlightthickness=1,highlightbackground=outline_collor,highlightcolor=outline_collor,foreground=text_color)
				text01.pack(side=tk.LEFT,padx=(1,2),pady=(2,2))
				text01.insert(0,result.get("chance"))
				text01.bind("<KeyRelease>", lambda event, vl = text01, cl = slot:services.set_result_pressing_chance(vl,cl))
				title03 = tk.Label(element_frame,text="%",width=1,background=light_bg_color,foreground=text_color)
				title03.pack(side=tk.LEFT,padx=(0,2),pady=(2,2))
				remove_button = tk.Button(element_frame,background=light_bg_color,activebackground=outline_collor,foreground=text_color,activeforeground="#000000",highlightbackground=outline_collor,highlightcolor=outline_collor,highlightthickness=1,text="Remove",width=6,command = lambda vl = slot:services.remove_result_pressing(vl,update=update_pressing_result))
				remove_button.pack(side=tk.LEFT,padx=(50,2),pady=(2,2))
				remove_buttons_elements.append(remove_button)
				titles_elements.append(title00)
				titles_elements.append(title02)
				titles_elements.append(title03)
				inputs_chance.append(text01)
				inputs_count.append(text00)
				element_database.append(slot)
				input_slot.append(slot)
			if update_images == True:
				services.update_pressing_slot_images(input_slot)
			element_database = element_database + inputs_count + inputs_chance + remove_buttons_elements + [add_button,module03_arrow00] + titles_elements
			inner_frame.update_idletasks()
			canvas.configure(scrollregion=canvas.bbox("all"))
		update_pressing_result(results)
	
	else:
		try:
			fn = playgrounds.get(str(modules))
			fn()
		except:
			pass

#TODO: adding new crafting elements



def load_crafting(name = False):
	global element_database, modules
	services.save_crafting(entry=recipe_name_entry.get())
	crafting_database = db_engine.load_crfating()
	names = crafting_database.keys()
	if name == False:
		load_item = easydialog.choicebox("choice item",options=list(names))
		if not load_item == None:
			pass
	else:
		load_item = name
	if not load_item == None:
		type = crafting_database.get(load_item).get("type")
		type_labbel.configure(text=f"Type: {str(type)}")
		type_labbel.text = f"Type: {str(type)}"
		if type == "crafting":
			modules = "crafting"
			update_workspace()
			services.load_crafting(load_item,element_database,recipe_name_entry)
		elif type == "crafting_shapeless":
			modules = "crafting_shapeless"
			update_workspace()
			services.load_crafting(load_item,element_database,recipe_name_entry)
		elif type == "mechanical_crafting":
			modules = "mechanical_crafting"
			update_workspace()
			services.load_crafting(load_item,element_database,recipe_name_entry)
		elif type == "furnace":
			modules = "furnace"
			update_workspace()
			services.load_crafting(load_item,element_database,recipe_name_entry)
		elif type == "pressing":
			modules = "pressing"
			update_workspace(results=crafting_database.get(load_item).get("results"))
			services.load_crafting(load_item,element_database,recipe_name_entry)
		elif type == "stonecutting":
			modules = "stonecutting"
			update_workspace()
			services.load_crafting(load_item,element_database,recipe_name_entry)
		elif type == "smithing_transform":
			modules = "smithing_transform"
			update_workspace()
			services.load_crafting(load_item,element_database,recipe_name_entry)
		elif type == "Custum Json":
			modules = "Custum Json"
			update_workspace()
			services.load_crafting(load_item,element_database,recipe_name_entry)
		elif type == "create_mixing":
			modules = "create_mixing"
			update_workspace()
			services.load_crafting(load_item,element_database,recipe_name_entry)
		elif type == "create_compacting":
			modules = "create_compacting"
			update_workspace()
			services.load_crafting(load_item,element_database,recipe_name_entry)
		elif type == "create_item_application":
			modules = "create_item_application"
			update_workspace(results=crafting_database.get(load_item).get("results"))
			services.load_crafting(load_item,element_database,recipe_name_entry)
		elif type == "create_deployng":	
			modules = "create_deployng"
			update_workspace(results=crafting_database.get(load_item).get("results"))
			services.load_crafting(load_item,element_database,recipe_name_entry)
		elif type == "create_crushing":
			modules = "create_crushing"
			update_workspace(results=crafting_database.get(load_item).get("results"))
			services.load_crafting(load_item,element_database,recipe_name_entry)
		elif type == "create_milling":
			modules = "create_crushing"
			update_workspace(results=crafting_database.get(load_item).get("results"))
			services.load_crafting(load_item,element_database,recipe_name_entry)
		elif type == "create_cutting":
			modules = "create_cutting"
			update_workspace(results=crafting_database.get(load_item).get("results"))
			services.load_crafting(load_item,element_database,recipe_name_entry)
		elif type == "Vortex":
			modules = "Vortex"
			update_workspace()
			services.load_crafting(load_item,element_database,recipe_name_entry)
		elif type == "Sequence Assembly":
			modules = "Sequence Assembly"
			update_workspace(results=crafting_database.get(load_item).get("results"))
			services.load_crafting(load_item,element_database,recipe_name_entry)
		elif type == "create_spouting":
			modules = "create_spouting"
			update_workspace(results=crafting_database.get(load_item).get("results"))
			services.load_crafting(load_item,element_database,recipe_name_entry)
		else:
			modules = type
			services.load_crafting(load_item,element_database,recipe_name_entry)
			update_workspace()

#TODO: add load crafting logic


def create_crafting():
	#,"Vortex"
	global aditional_types
	type = easydialog.choicebox("Choice Item Type",options=["crafting_shaped","crafting_shapeless","mechanical_crafting","furnace","stonecutting","smithing_transform","pressing","create_mixing","create_compacting","create_item_application","create_deployng","create_crushing","create_milling","create_cutting","create_spouting","sequence_assembly","custum_json"] + aditional_types,prompt="Choice Item Type")
	if type == "crafting_shaped":
		type = "crafting"
	elif type == "sequence_assembly":
		type = "Sequence Assembly"
	elif type == "custum_json":
		type = "Custum Json"
	if not type == None:
		name = easydialog.enterbox("Enter Name","Enter Name")
		if name == "":
			name = str(uuid.uuid4())
		services.create_crafting_palet(type,name,load_crafting,update_selector_list)	

#TODO: adding craftings



def create_tab_bar(root,remove_func,click_func):
	main_tab_frame = tk.Frame(root,bg=dark_bg_color) #tab bar bg
	main_tab_frame.pack(fill="x", side="top",padx=(200,5))
	canvas = tk.Canvas(main_tab_frame, height=30,bg=dark_bg_color,highlightbackground=outline_collor,highlightcolor=outline_collor,highlightthickness=1) #tab bar bg
	scrollbar = tk.Scrollbar(main_tab_frame, orient="horizontal", command=canvas.xview,width=7,background=dark_bg_color,highlightbackground=outline_collor,highlightcolor=outline_collor,highlightthickness=1,activebackground=outline_collor)
	canvas.configure(xscrollcommand=scrollbar.set)
	scrollbar.pack(side="bottom", fill="x",pady=(2,0))
	canvas.pack(fill="x", side="top")

	tab_frame = tk.Frame(canvas,background=dark_bg_color)
	canvas.create_window((0, 0), window=tab_frame, anchor="nw")

	def update_canvas():
		tab_frame.update_idletasks()
		canvas.config(scrollregion=canvas.bbox("all"))

	def add_tab_button(tab_text):
		single_tab = tk.Frame(tab_frame,bg=dark_bg_color,highlightbackground=outline_collor,highlightcolor=outline_collor,highlightthickness=1)
		single_tab.pack(side="left", padx=2,pady=(2,2))

		tab_button = tk.Button(single_tab,text=tab_text, command=lambda: on_tab_click(tab_text),foreground=text_color,background=light_bg_color,highlightbackground=outline_collor,highlightcolor=outline_collor,highlightthickness=0,font=("Arial", 8))
		tab_button.pack(side="left", padx=2)

		close_button = tk.Button(single_tab, text="X", width=2, command=lambda: remove_tab(tab_text, single_tab),foreground=text_color,background=light_bg_color,highlightbackground=outline_collor,highlightcolor=outline_collor,highlightthickness=0,font=("Arial", 8))
		close_button.pack(side="left",padx = (0,2))

	def on_tab_click(tab_text):
		click_func(tab_text)

	def remove_tab(tab_text, frame):
		frame.destroy()
		update_canvas()
		remove_func(tab_text)
	update_canvas()

	
	# Funkce pro skrolování pomocí kolečka myši
	def on_mouse_wheel(event):
		try:
			if event.delta:
				canvas.xview_scroll(int(-1*(event.delta/120)), "units")
				scrollbar.set(canvas.xview())
			elif event.num == 4:
				canvas.xview_scroll(-1, "units")
				scrollbar.set(canvas.xview())
			elif event.num == 5:
				canvas.xview_scroll(1, "units")
				scrollbar.set(canvas.xview())
		except:
			pass

	main_tab_frame.bind_all("<MouseWheel>", on_mouse_wheel)
	main_tab_frame.bind_all("<Button-4>", on_mouse_wheel)  # Pro Linux (kolečko nahoru)
	main_tab_frame.bind_all("<Button-5>", on_mouse_wheel)


	return update_canvas, add_tab_button



project_selector_frame=ctk.CTkFrame(root_window)
project_selector_frame.place(y=610,x=10)

project_selector_search = ctk.CTkEntry(project_selector_frame)
project_selector_search.pack(pady=(2,2),padx=(2,2),fill="x")
services.shortcut(project_selector_search)
project_selector_list = tk.Listbox(project_selector_frame,width=20,height=10,background=dark_bg_color,foreground=text_color,highlightbackground=outline_collor,highlightcolor=outline_collor,highlightthickness=1,selectbackground=outline_collor,selectforeground=text_color)
project_selector_list.pack(pady=(0,2),padx=(2,2))

def load_selected_crafting(event):
	selection = project_selector_list.curselection()
	if selection:
		index = selection[0]
		selected_item = project_selector_list.get(index)
		load_crafting(name=str(selected_item))

def update_search(event):
	search_data = str(project_selector_search.get()).lower()
	results = []
	crafting_database = db_engine.load_crfating()
	database = crafting_database.keys()
	for i in database:
		if search_data in str(i):
			results.append(i)
	project_selector_list.delete(0,tk.END)
	for i in results:
		project_selector_list.insert(tk.END,i)

project_selector_search.bind("<KeyRelease>",update_search)
project_selector_list.unbind("<<ListboxSelect>>")
project_selector_list.bind("<<ListboxSelect>>",load_selected_crafting)

def update_selector_list():
	crafting_database = db_engine.load_crfating()
	data = crafting_database.keys()
	project_selector_list.delete(0,tk.END)
	for i in data:
		project_selector_list.insert(tk.END,i)

update_selector_list()

root_menu=tk.Menu(root)
root_window.config(menu=root_menu)
root_menu.config(background=light_bg_color,activebackground=outline_collor)

root_menu_file=tk.Menu(root_menu,background=light_bg_color,activebackground=outline_collor,tearoff=0)
root_menu_file.add_separator()

root_menu_quick_tools=tk.Menu(root_menu,background=light_bg_color,activebackground=outline_collor,tearoff=0)
root_menu_quick_tools.add_separator()

def remove_crafting():
	services.remove_crfating(recipe_name_entry.get())
	update_selector_list()
	clear_workspace()
	recipe_name_entry.delete(0,tk.END)

def save_data():
	save_tags_edits()
	update_tag_database()
	update_removed_ids()
	update_hide_c()
	services.save_crafting()
def rename_crafting():
	def_name = recipe_name_entry.get()
	name = easydialog.editbox("Rename Crafting",editable_text=str(def_name))
	services.create_name(str(name))
	services.remove_crfating(str(def_name))
	save_data()
	update_selector_list()

#---
root_menu_file.add_command(label="Save",foreground=text_color,command=save_data)
root_menu_file.add_command(label="New...",foreground=text_color,command=create_crafting)
root_menu_file.add_command(label="Remove Crafting",foreground=text_color,command=remove_crafting)
root_menu_file.add_command(label="Rename Crafting",foreground=text_color,command=rename_crafting)
root_menu_file.add_command(label="Compile",foreground=text_color,command=lambda: services.export())
root_menu_file.add_command(label="Update Database",foreground=text_color,command=update_database)
root_menu_file.add_command(label="Exit To Louncher",foreground=text_color,command=tolouncher)

def json_auti_correct_toogle():
	global auto_indent_correct
	if auto_indent_correct:
		auto_indent_correct = False
	else:
		auto_indent_correct = True
	print(f"auto tags json correct: {auto_indent_correct}")


root_menu_quick_tools.add_command(label="Toogle JAIC",command=json_auti_correct_toogle)
root_menu_quick_tools.add_command(label="Correct Json Tags",command=lambda: json_auto_indent_correct(tags_edit_textbox,True))



def clear_workspace():

	for element in element_database:
		try:
			element.destroy()
		except:
			pass




recipe_name_frame = ctk.CTkFrame(root,width=190,height=555)
recipe_name_frame.pack(fill="y",anchor="e",side="left",pady=4,padx=4)
recipe_name_entry = ctk.CTkEntry(recipe_name_frame)

recipe_name_entry.pack_propagate(0)

type_labbel = ctk.CTkLabel(recipe_name_frame,text="Type: ")
type_labbel.pack(fill="x",pady=4,padx=4)

root_window.bind_all("<Control-s>",lambda event:save_data())
root_window.bind_all("<Control-n>",lambda event:create_crafting())
root_window.bind_all("<Control-q>",lambda event:services.export(generators))
root_window.bind_all("<Control-r>",lambda event:update_database())

root_menu.add_cascade(label="File",foreground=text_color,menu=root_menu_file)
#root_menu.add_cascade(label="Quick Tools",foreground=text_color,menu=root_menu_quick_tools)

#system plugins



#plugins
PLUGINS_DIR = "plugins"

def load_plugins():
	plugins = []
	for filename in os.listdir(PLUGINS_DIR):
		if filename.endswith(".py") and filename != "__init__.py":
			plugin_name = filename[:-3]
			module = importlib.import_module(f"{PLUGINS_DIR}.{plugin_name}")
			plugins.append(module)
	return plugins

plugins = load_plugins()

plugins_command = 0
for plugin in plugins:
	if hasattr(plugin,"runDialog"):
		plugins_command += 1

if plugins_command > 0:
	root_menu_plugins=tk.Menu(root_menu,background=light_bg_color,activebackground=outline_collor,tearoff=0)
	root_menu_plugins.add_separator()
	root_menu.add_cascade(label="Plugins",foreground=text_color,menu=root_menu_plugins)


generators={}
plugins_updates = []
for plugin in plugins:
	if hasattr(plugin,"run"):
		plugin.run()
	if hasattr(plugin,"Tab"):
		pl_fr = ctk.CTkFrame(tab_menu,width=1000,height=600)
		pl_fr.place(y=1,x=10)
		tab_menu.add(pl_fr,text=plugin.TAB_NAME)
		plugin.Tab(pl_fr)
	
	if hasattr(plugin,"runDialog"):
		root_menu_plugins.add_command(label=str(plugin.RUN_DIALOG_NAME),foreground=text_color,command=lambda pl = plugin: pl.runDialog())
	if hasattr(plugin,"update"):
		plugins_updates.append(plugin)
	if hasattr(plugin,"PlayGround") and hasattr(plugin,"Generator"):
		plg_type = next(iter(plugin.SCRUCTURE))
		playgrounds[plg_type]=plugin.PlayGround
		generators[plg_type]=plugin.Generator
	
print(f"[Plugins Loaded]: {str(len(plugins))}")

def plugins_updates_run():
	global plugins_updates,running
	while running:
		for plugin in plugins_updates:
			plugin.update()
		time.sleep(0.1)
pl_update = threading.Thread(target=plugins_updates_run)
pl_update.start()

print(f"[info]: server connection = {db_engine.SERVER_CONNECTION}")

def auto_refresh():
	global running
	while running:
		if project_selector_search.get() == "":
			update_selector_list()
		#if not tab_menu.index("current") == 2:
			#load_array_textbox(tags_textbox,database_loader.load_tags())
		if not tab_menu.index("current") == 3:
			tags_edit_textbox.delete(0.0,ctk.END)
			tags_edit_textbox.insert(0.0,json.dumps(db_engine.load_tags_edits(),indent="\t"))
			update_custum_parms(tags_editor_commander,tags_edit_textbox.get(0.0,ctk.END))

		if not tab_menu.index("current") == 1:
			load_array_textbox(remove_textbox,db_engine.load_removed_crfating_ids())
		if not tab_menu.index("current") == 4:
			load_array_textbox(hide_c_textbox,db_engine.load_hidden_crfating_ids())
		time.sleep(db_engine.REFRESH_RATIO)

if db_engine.SERVER_CONNECTION:
	print("[info] creating auto refresh threading")
	art = threading.Thread(target=auto_refresh)
	print("[info] auto refresh threading created")
	print("[info] starting auto refresh threading")
	art.start()
	print("[info] auto refresh threading started")




root_window.mainloop()


