from core import DataAPI
from core import services
from core import generator
import tkinter as tk
from core import db_engine
import os
import json
from PIL import Image,ImageTk
import customtkinter as ctk
from core.ui import colorschem
outline_collor = colorschem.outline_collor
dark_bg_color = colorschem.dark_bg_color
light_bg_color = colorschem.light_bg_color
I_slot00=ImageTk.PhotoImage(Image.open("assets/textures/slot00.png").resize((54,54),resample=0))


class MouseWheelFixer:
	def __init__(self, scrollable_frame):
		self.scrollable_frame = scrollable_frame
		self.canvas = scrollable_frame._parent_canvas

		# Povol focus, jinak se kolečko nebude chytat
		self.canvas.bind("<Enter>", self._bind_mousewheel)
		self.canvas.bind("<Leave>", self._unbind_mousewheel)

	def _bind_mousewheel(self, event):
		self.canvas.bind_all("<MouseWheel>", self._on_mousewheel_windows)  # Windows/macOS
		self.canvas.bind_all("<Button-4>", self._on_mousewheel_linux)	  # Linux scroll up
		self.canvas.bind_all("<Button-5>", self._on_mousewheel_linux)	  # Linux scroll down

	def _unbind_mousewheel(self, event):
		self.canvas.unbind_all("<MouseWheel>")
		self.canvas.unbind_all("<Button-4>")
		self.canvas.unbind_all("<Button-5>")

	def _on_mousewheel_windows(self, event):
		self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

	def _on_mousewheel_linux(self, event):
		direction = -1 if event.num == 4 else 1
		self.canvas.yview_scroll(direction, "units")


def error(i):
	print(f"[error]: {i}")
def info(i):
	print(f"[info]: {i}")
def ok(i):
	print(f"[ok]: {i}")

def AddElements(element):
	DataAPI.add_in_to_elements_list_func(element)

def GetPlayground():
	return DataAPI.get_crafting_arena

def GetID(ID):
	return services.crafting.get(ID)

def CreateScructure(Scructure={}):
	DataAPI.add_in_to_additional_types_func([next(iter(Scructure))])
	services.AddIntoDataScructures(next(iter(Scructure)),Scructure.get(next(iter(Scructure))))

class caption(ctk.CTkLabel):
	def __init__(self,text,x,y, width = 0, height = 28):
		super().__init__(master=GetPlayground(), width=width, height=height,text=text)
		self.x = x
		self.y= y
		AddElements(self)
		self.place(x=self.x,y=self.y)
	def update_text(self,text):
		self.configure(text=text)
		self.text=text

class ItemInput(tk.Button):
	def __init__(self, id,x,y):
		super().__init__(master = GetPlayground(),command=self.update_Item_Input,highlightbackground=outline_collor,highlightcolor=outline_collor,background=light_bg_color,image=I_slot00,borderwidth=0,highlightthickness=1)
		AddElements(self)
		self.id = id
		self.x = x
		self.y = y
		self.place(x=self.x,y=self.y)
		try:
			selected_minecraft_item = services.crafting.get(self.id)
			selected_item = services.remove_mod(selected_minecraft_item)
			tag = False
			if str(selected_minecraft_item).startswith("tag:"):
				tag = True

			preview_image_button = ImageTk.PhotoImage(Image.open(db_engine.search_path(selected_item,tag=tag)).resize((54,54),resample=0))
			self.config(image=preview_image_button)
			self.image = preview_image_button
		except:
			self.config(image=I_slot00)
			self.image = I_slot00
	def update_Item_Input(self):
		try:
			selected_minecraft_item = services.get_selected_item()
			if selected_minecraft_item == None:
				services.update_crafting_key(self.id,"")
				self.config(image=I_slot00)
				self.image = I_slot00
			else:
				services.update_crafting_key(self.id,selected_minecraft_item)
				selected_item = services.remove_mod(selected_minecraft_item)
				tag = False
				if str(selected_minecraft_item).startswith("tag:"):
					tag = True
				
				preview_image_button = ImageTk.PhotoImage(Image.open(db_engine.search_path(selected_item,tag=tag)).resize((54,54),resample=0))
				self.config(image=preview_image_button)
				self.image = preview_image_button
				ok(services.crafting)
		except:
			pass

class Input(ctk.CTkEntry):
	def __init__(self,id,x,y,width=160):
		super().__init__(master=GetPlayground(),width=width)
		AddElements(self)
		self.id = id
		self.x = x
		self.y = y
		self.place(x=self.x,y=self.y)
		self.bind("<KeyRelease>",self.update_entry)
		try:
			self.delete(0,ctk.END)
			self.insert(0,services.crafting.get(self.id))
		except:
			self.delete(0,ctk.END)

	def update_entry(self,v):
		services.update_crafting_key(self.id,self.get())


class OptionMenu(ctk.CTkOptionMenu):
	def __init__(self,id,options,x,y,width = 140, height = 28):
		super().__init__(master = GetPlayground(), width = width, height = height,command=self.callback,values=options)
		AddElements(self)
		self.options = options
		self.x = x
		self.y = y
		self.id = id
		self.place(x=self.x,y=self.y)
		try:
			self.set(services.crafting.get(self.id))
		except:
			pass
	def callback(self,value):
		services.update_crafting_key(self.id,value)


class CheckBox(ctk.CTkCheckBox):
	def __init__(self, id,text,x,y, width = 100, height = 24):
		super().__init__(master=GetPlayground(), width=width, height=height,text=text,onvalue="1",offvalue="0",command=self.callback)
		AddElements(self)
		self.id = id
		self.x = x
		self.y = y
		self.var = ctk.StringVar(value="0")
		self.configure(variable=self.var)
		self.place(x=self.x,y=self.y)
		try:
			self.var.set(services.crafting.get(self.id))
			self.update()
		except:
			pass
	def callback(self):
		services.update_crafting_key(self.id,self.var.get())

class Switch(ctk.CTkSwitch):
	def __init__(self, id,text,x,y, width = 100, height = 24):
		super().__init__(master=GetPlayground(), width=width, height=height,text=text,onvalue="1",offvalue="0",command=self.callback)
		AddElements(self)
		self.id = id
		self.x = x
		self.y = y
		self.var = ctk.StringVar(value="0")
		self.configure(variable=self.var)
		self.place(x=self.x,y=self.y)
		try:
			self.var.set(services.crafting.get(self.id))
			self.update()
		except:
			pass
	def callback(self):
		services.update_crafting_key(self.id,self.var.get())



class Slider(ctk.CTkSlider):
	def __init__(self,id,min,max,x,y,width = 200, height = 20,orientation = "horizontal"):
		super().__init__(master = GetPlayground(), width = width, height = height,command=self.callback,from_=min,to=max,orientation=orientation)
		AddElements(self)
		self.x = x
		self.y = y
		self.id = id
		self.place(x=self.x,y=self.y)
		try:
			self.set(services.crafting.get(self.id))
		except:
			pass
	def callback(self,value):
		services.update_crafting_key(self.id,value)


class ResultsInput(ctk.CTkFrame):  # Hlavní rám
	def __init__(self, id, x, y):
		super().__init__(master=GetPlayground())  
		self.place(x=x, y=y)

		self.parent_frame = ctk.CTkFrame(self)  # Vnější rám
		self.parent_frame.pack(fill="both", expand=True, padx=5, pady=5)

		self.scrollable_frame = ctk.CTkScrollableFrame(self.parent_frame,border_width=0,width=650)  # ScrollableFrame
		self.scrollable_frame.pack(fill="both", expand=True)
		MouseWheelFixer(self.scrollable_frame)
		AddElements(self) 
		AddElements(self.parent_frame)  # Přidává prvky do parent_frame

		self.id = id
		self.update_fn()

	def update_fn(self):
		for element in self.scrollable_frame.winfo_children():
			element.destroy()

		self.results = services.crafting.get(self.id)
		info(self.results)
		self.loop = 0

		for res in self.results:
			frame = ctk.CTkFrame(self.scrollable_frame)  # Vkládání do scrollable_frame
			frame.pack(fill="x", side="top", pady=5, padx=5)

			slot = tk.Button(
				frame, image=I_slot00, borderwidth=0, highlightthickness=1, 
				highlightbackground=outline_collor, highlightcolor=outline_collor, 
				background=light_bg_color
			)
			slot.pack(side="left", padx=5, pady=5)
			slot.config(command=lambda b=slot, l=self.loop: self.update_slot(b, l))

			try:
				selected_minecraft_item = res.get("item")
				selected_item = services.remove_mod(selected_minecraft_item)
				tag = selected_minecraft_item.startswith("tag:")
				preview_image_button = ImageTk.PhotoImage(
					Image.open(db_engine.search_path(selected_item, tag=tag)).resize((54, 54), resample=0)
				)
				slot.config(image=preview_image_button)
				slot.image = preview_image_button
			except:
				slot.config(image=I_slot00)
				slot.image = I_slot00

			l1 = ctk.CTkLabel(frame,text="Count: ")
			l1.pack(side="left",pady=5,padx=2)
			i1 = ctk.CTkEntry(frame)
			i1.pack(side="left",pady=5,padx=2)
			l2 = ctk.CTkLabel(frame,text="Chance: ")
			l2.pack(side="left",pady=5,padx=2)
			i2 = ctk.CTkEntry(frame)
			i2.pack(side="left",pady=5,padx=2)
			i1.bind("<KeyRelease>", lambda v, i1=i1, ii=self.loop, inn="count": self.update_i(i1, ii, inn))
			i2.bind("KeyRelease", lambda v, i2=i2, ii=self.loop, inn="chance": self.update_i(i2, ii, inn))
			try:
				i1.delete(0,ctk.END)
				i1.insert(0,res.get("count"))
			except:
				pass
			try:
				i2.delete(0,ctk.END)
				i2.insert(0,res.get("chance"))
			except:
				pass

			del_button = ctk.CTkButton(frame, text="Delete", command=lambda r=res: self.delete(r))
			del_button.pack(side="left", pady=5, padx=5)

			self.loop += 1
		
		self.add_button = ctk.CTkButton(self.scrollable_frame, text="Add", command=self.add)
		self.add_button.pack(side="top", fill="x", padx=5, pady=5)

	def delete(self, r):
		self.results = services.crafting.get(self.id)
		self.results.remove(r)
		services.update_crafting_key(self.id, self.results)
		self.update_fn()

	def add(self):
		self.results = services.crafting.get(self.id)
		self.results.append({"item": "", "count": 1, "chance": 100})
		services.update_crafting_key(self.id, self.results)
		self.update_fn()

	def update_slot(self, button, index):
		try:
			self.results = services.crafting.get(self.id)
			selected_minecraft_item = services.get_selected_item()
			self.results[index]["item"] = selected_minecraft_item
			services.update_crafting_key(self.id, self.results)
			selected_item = services.remove_mod(selected_minecraft_item)
			tag = selected_minecraft_item.startswith("tag:")
			preview_image_button = ImageTk.PhotoImage(
				Image.open(db_engine.search_path(selected_item, tag=tag)).resize((54, 54), resample=0)
			)
			button.config(image=preview_image_button)
			button.image = preview_image_button
		except:
			button.config(image=I_slot00)
			button.image = I_slot00
	
	def update_i(self,i,index,inn):
		try:
			self.results = services.crafting.get(self.id)
			self.results[index][inn] = i.get()
			print(i.get())
			services.update_crafting_key(self.id, self.results)
		except:
			pass


class FileAccessManager():
	def __init__(self,file,empty={}):
		self.empty = empty
		self.file = os.path.join(db_engine.projects_path,db_engine.project_name,file)
		self.check_file()
	def check_file(self):
		if not os.path.exists(self.file):
			self.create_empty()
	def create_empty(self):
		self.write(self.empty)
	def write(self,data):
		with open(self.file,"w") as f:
			f.write(json.dumps(data,indent="\t"))
	def read(self):
		data = {}
		with open(self.file) as f:
			data = json.loads(f.read())
		return data


