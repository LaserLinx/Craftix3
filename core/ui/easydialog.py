import tkinter as tk
from core import DataAPI
import tkinter as tk
from core.ui import colorschem

outline_collor = colorschem.outline_collor
dark_bg_color = colorschem.dark_bg_color
light_bg_color = colorschem.light_bg_color
text_color = colorschem.text_color

class shortcut():
	def __init__(self,widget):
		self.widget = widget
		self.widget.bind("<Control-a>",self.select_all)
	
	def select_all(self,event):
			event.widget.select_range(0, tk.END)
			event.widget.icursor(tk.END)
			return "break"



def choicebox(title, options, prompt="pick an item", bg="#333333", fg="#eeeeee"):
	result = [None]
	filtered_options = options[:]

	def update_listbox(search_term):
		"""Aktualizuje Listbox na základě hledaného výrazu."""
		listbox.delete(0, tk.END)
		for option in filtered_options:
			if search_term.lower() in option.lower():
				listbox.insert(tk.END, option)

	def on_search(event):
		"""Funkce pro zpracování vyhledávání."""
		search_term = search_var.get()
		update_listbox(search_term)

	def on_ok(event=None):
		"""Uložení vybrané možnosti a zavření okna."""
		selection = listbox.curselection()
		if selection:
			result[0] = listbox.get(selection[0])
		root.destroy()

	def set_focus(event=None):
		search_entry.focus_set()

	def on_cancel(event=None):
		"""Zrušení výběru a zavření okna."""
		root.destroy()

	def move_selection_down(event=None):
		current_selection = listbox.curselection()
		if current_selection:
			next_index = current_selection[0] + 1
			if next_index < listbox.size():
				listbox.select_clear(current_selection)
				listbox.select_set(next_index)
				listbox.activate(next_index)
		else:
			if listbox.size() > 0:
				listbox.select_set(0)
				listbox.activate(0)
		listbox.focus_set()  # Přepnutí fokus na listbox

	def move_selection_up(event=None):
		current_selection = listbox.curselection()
		if current_selection:
			prev_index = current_selection[0] - 1
			if prev_index >= 0:
				listbox.select_clear(current_selection)
				listbox.select_set(prev_index)
				listbox.activate(prev_index)
		else:
			if listbox.size() > 0:
				listbox.select_set(listbox.size() - 1)
				listbox.activate(listbox.size() - 1)
		listbox.focus_set()  # Přepnutí fokus na listbox

	root = tk.Frame(DataAPI.root,background=dark_bg_color,highlightbackground=outline_collor,highlightcolor=outline_collor,highlightthickness=1)
	root.place(x=865,y=425)
	root.focus_set()
	root.grab_set()
	tk.Label(root, text=prompt, bg=bg, fg=fg).pack(pady=10)

	search_var = tk.StringVar()
	search_entry = tk.Entry(root, textvariable=search_var, bg='#444444', fg=fg, insertbackground=fg)
	search_entry.pack(pady=5)
	shortcut(search_entry)
	search_entry.bind('<KeyRelease>', on_search)

	listbox = tk.Listbox(root, selectmode=tk.SINGLE, bg=bg, fg=fg, highlightbackground="#00cccc",
						 highlightcolor="#00cccc", selectbackground="#00cccc")
	listbox.pack(pady=10, fill=tk.BOTH, expand=True)
	update_listbox('')
	listbox.selection_set(0)

	button_frame = tk.Frame(root, bg=bg)
	tk.Button(button_frame, text="OK", width=10, command=on_ok, bg='lightgreen').pack(side=tk.LEFT, padx=5, pady=5)
	tk.Button(button_frame, text="Cancel", width=10, command=on_cancel, bg='lightcoral').pack(side=tk.RIGHT, padx=5, pady=5)

	root.bind("<Return>", on_ok)
	root.bind("<Escape>", on_cancel)
	root.bind("<Control-f>", set_focus)
	root.bind("<Down>", move_selection_down)
	root.bind("<Up>", move_selection_up)
	button_frame.pack()

	root.wait_window()
	return result[0]





def msgbox(message, title="info", bg="#222222", fg="#eeeeee"):
	def on_ok(event=None):
		root.destroy()

	root = tk.Frame(DataAPI.root,background=dark_bg_color,highlightbackground=outline_collor,highlightcolor=outline_collor,highlightthickness=1)
	root.place(x=865,y=425)
	root.focus_set()
	tk.Label(root, text=message, bg=bg, fg=fg).pack(padx=20, pady=20)
	tk.Button(root, text="OK", command=on_ok, bg='#222222', activebackground="#333333", activeforeground="#eeeeee", fg='#eeeeee', highlightbackground="#00cccc", highlightcolor="#00cccc", highlightthickness=1).pack(pady=10)
	root.bind("<Return>",on_ok)
	root.bind("<Escape>",on_ok)
	root.grab_set()  # Nastaví okno jako modální
	root.wait_window()
		
def buttonbox(msg, title="Choose an option", choices=None):
	if choices is None:
		choices = ["OK"]
	result = [None]
	def on_button_click(choice):
		result[0] = choice
		root.destroy()

	root = tk.Frame(DataAPI.root,background=dark_bg_color,highlightbackground=outline_collor,highlightcolor=outline_collor,highlightthickness=1)
	root.place(x=865,y=425)
	root.focus_set()
	tk.Label(root, text=msg,background="#222222",foreground="#eeeeee").pack(pady=10)
	root.bind("<Return>",lambda event:on_button_click(choices[0]))
	root.bind("<Escape>",lambda event:on_button_click(choices[1]))
	for choice in choices:
		tk.Button(root, text=choice, command=lambda c=choice: on_button_click(c),background="#222222",highlightbackground="#00cccc",highlightcolor="#00cccc",highlightthickness=1,foreground="#eeeeee",activeforeground="#eeeeee",activebackground="#333333").pack(side=tk.LEFT, padx=5)

	
	root.wait_window()
	root.destroy()
	return result[0]

def enterbox(msg, title="Enter Input", bg="#222222", fg="#eeeeee"):
	result = [None]
	def on_ok(event=None):
		result[0] = entry.get()
		root.destroy()
		
	root = tk.Frame(DataAPI.root,background=dark_bg_color,highlightbackground=outline_collor,highlightcolor=outline_collor,highlightthickness=1)
	root.pack(side="bottom",anchor="center",pady=(0,10))
	root.focus_set()
	tk.Label(root, text=f"\n\n{msg}\n\n", bg=bg, fg=fg).pack(pady=10)
	entry = tk.Entry(root, bg='#333333', fg=fg, insertbackground=fg,highlightbackground="#00cccc",highlightcolor="#00cccc",highlightthickness=1,width=120)
	shortcut(entry)
	entry.pack(pady=10)
	entry.focus_set()
	tk.Button(root, text="OK", command=on_ok, bg='#444444', fg='#eeeeee',highlightbackground="#00cccc",highlightcolor="#00cccc",highlightthickness=1,activebackground="#333333",activeforeground="#eeeeee").pack(pady=10)
	root.bind_all('<Return>',on_ok)
	root.bind_all("<Escape>",lambda event:root.destroy())
	root.bind_all("<Control-a>",lambda event: entry.selection_range(0,tk.END))
	root.wait_window()
	return result[0]

def editbox(msg, title="Enter Input", bg="#222222", fg="#eeeeee",editable_text = "edit text"):
	result = [None]
	def on_ok(event=None):
		result[0] = entry.get()
		root.destroy()
	root = tk.Frame(DataAPI.root,background=dark_bg_color,highlightbackground=outline_collor,highlightcolor=outline_collor,highlightthickness=1)
	root.pack(side="bottom",anchor="center",pady=(0,10))
	root.focus_set()
	tk.Label(root, text=f"\n\n{msg}\n\n", bg=bg, fg=fg).pack(pady=10)
	entry = tk.Entry(root, bg='#333333', fg=fg, insertbackground=fg,highlightbackground="#00cccc",highlightcolor="#00cccc",highlightthickness=1,width=120)
	entry.insert(0,str(editable_text))
	shortcut(entry)
	entry.pack(pady=10)
	entry.focus_set()
	tk.Button(root, text="OK", command=on_ok, bg='#444444', fg='#eeeeee',highlightbackground="#00cccc",highlightcolor="#00cccc",highlightthickness=1,activebackground="#333333",activeforeground="#eeeeee").pack(pady=10)
	root.bind_all('<Return>',on_ok)
	root.bind_all("<Escape>",lambda event:root.destroy())
	root.bind_all("<Control-a>",lambda event: entry.selection_range(0,tk.END))
	root.wait_window()
	return result[0]




