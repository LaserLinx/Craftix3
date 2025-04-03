import os
import requests
import customtkinter as ctk
from tkinter import messagebox
import shutil
# GitHub repo settings
OWNER = "LaserLinx"
REPO = "CraftixPlugins"
BRANCH = "main"
GITHUB_API_URL = f"https://api.github.com/repos/{OWNER}/{REPO}/contents/"

# Plugin directories
PLUGINS_DIR = "plugins"
DISABLED_DIR = "disabled_plugins"

# Ensure directories exist
os.makedirs(PLUGINS_DIR, exist_ok=True)
os.makedirs(DISABLED_DIR, exist_ok=True)

def fetch_plugins():
	try:
		response = requests.get(GITHUB_API_URL)
		if response.status_code == 200:
			return [plugin["name"] for plugin in response.json() if plugin["name"].endswith(".py")]
		else:
			messagebox.showerror("Error", "Failed to fetch plugins from GitHub")
			return []
	except Exception as e:
		messagebox.showerror("Error", f"Exception: {e}")
		return []

def download_plugin(plugin_name):
	try:
		response = requests.get(GITHUB_API_URL)
		if response.status_code == 200:
			plugins = response.json()
			for plugin in plugins:
				if plugin["name"] == plugin_name:
					url = plugin["download_url"]
					filepath = os.path.join(PLUGINS_DIR, plugin_name)
					
					plugin_response = requests.get(url)
					if plugin_response.status_code == 200:
						with open(filepath, "wb") as f:
							f.write(plugin_response.content)
						messagebox.showinfo("Success", f"Plugin {plugin_name} downloaded successfully!")
						return
					else:
						messagebox.showerror("Error", "Failed to download plugin")
						return
			messagebox.showerror("Error", f"Plugin {plugin_name} not found!")
		else:
			messagebox.showerror("Error", "Failed to fetch plugin list from GitHub")
	except Exception as e:
		messagebox.showerror("Error", f"Exception: {e}")


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("./assets/themes/default.json")
root = ctk.CTk()
root.geometry("500x300")
root.title("Craftix3 PLuginManager v1.0")
tabs = ctk.CTkTabview(root,border_width=0)
tabs.pack(fill="x")
tabs.add("Download Plugins")
tabs.add("Manage Plugins")
tabs.set("Manage Plugins")

download_plugins_frame = tabs.tab("Download Plugins")
Manage_Plugins_frame = tabs.tab("Manage Plugins")

#Manage Plugins
Manager = ctk.CTkScrollableFrame(Manage_Plugins_frame)
Manager.pack(fill="both")


class plugin(ctk.CTkFrame):
	def __init__(self,master,name,activate):
		super().__init__(master)
		self.name=name
		self.activate = activate
		l=ctk.CTkLabel(self,text=str(self.name).replace(".py",""))
		l.pack(side="left",pady=5,padx=5)
		self.switch_var = ctk.BooleanVar(value=activate)
		self.switch = ctk.CTkSwitch(self,command=self.callback,onvalue=True,offvalue=False,variable=self.switch_var,width=75)
		self.switch.pack(side="right",pady=5,padx=1)
		ctk.CTkLabel(self,text="|",text_color="#00ffff").pack(side="right")
		ctk.CTkButton(self,text="Delete",command=self.delete,width=70).pack(side="right",pady=(2,2),padx=5)
		self.update_switch()
	def callback(self):
		self.activate = self.switch_var.get()
		if self.switch_var.get():
			shutil.move(os.path.join(DISABLED_DIR,self.name),PLUGINS_DIR)
		else:
			shutil.move(os.path.join(PLUGINS_DIR,self.name),DISABLED_DIR)
		self.update_switch()

	def update_switch(self):
		text=""
		if self.switch_var.get():
			text="on"
		else:
			text="off"
		self.switch.configure(text=text)
	
	def delete(self):
		if self.activate:
			os.remove(os.path.join(PLUGINS_DIR,self.name))
		else:
			os.remove(os.path.join(DISABLED_DIR,self.name))
		update_download()
		self.destroy()

active_plugins = os.listdir(PLUGINS_DIR)
deactivate_plugins = os.listdir(DISABLED_DIR)

def update_Manager():
	global active_plugins,deactivate_plugins
	active_plugins = os.listdir(PLUGINS_DIR)
	deactivate_plugins = os.listdir(DISABLED_DIR)
	for widget in Manager.winfo_children():
		widget.destroy()

	for pl in active_plugins:
		if not str(pl) in ["__init__.py","__pycache__"]:
			plugin(Manager,str(pl),True).pack(pady=1,padx=(1,8),fill="x")

	for pl in deactivate_plugins:
		if not str(pl) in ["__init__.py","__pycache__"]:
			plugin(Manager,str(pl),False).pack(pady=1,padx=(1,8),fill="x")

update_Manager()

#download plugins
download_manager = ctk.CTkScrollableFrame(download_plugins_frame)
download_manager.pack(fill="both")

class plugin_download(ctk.CTkFrame):
	def __init__(self,master,name):
		super().__init__(master)
		self.name = name
		l=ctk.CTkLabel(self,text=str(self.name).replace(".py",""))
		l.pack(side="left",pady=5,padx=5)
		ctk.CTkButton(self,text="Download",command=self.download).pack(side="right",pady=(2,2),padx=5)

	def download(self):
		print(self.name)
		download_plugin(self.name)
		update_Manager()
		self.destroy()


def update_download():
	active_plugins = os.listdir(PLUGINS_DIR)
	deactivate_plugins = os.listdir(DISABLED_DIR)
	exists_plugins = active_plugins + deactivate_plugins
	for widget in download_manager.winfo_children():
		widget.destroy()
	for pl in fetch_plugins():
		if not pl in exists_plugins:
			plugin_download(download_manager,pl).pack(pady=1,padx=(1,8),fill="x")
	if len(download_manager.winfo_children()) == 0:
		ctk.CTkLabel(download_manager,text="Any Plugins Not Aviable.").pack(fill="both")

update_download()

root.mainloop()

