import tkinter as tk

x = 20
y = 20
height = 5
width = 5
def center(screen,object):
	global x,y,height,width

	def center(move):
		global x,y,height,width
		if move == "up":
			y = y - 1
		if move == "down":
			y = y + 1
		if move == "left":
			x = x - 1
		if move == "right":
			x = x + 1
		if move == "h+":
			height = height + 1
		if move == "h-":
			height = height - 1
		if move == "w+":
			width = width + 1
		if move == "w-":
			width = width - 1
		object.place(x=x,y=y)
		#object.config(height=height,width=width)
		

		print(f"place info: x: {x},y: {y}, h:{height}, w:{width}")

	screen.bind("<Control-a>", lambda event: center("left"))
	screen.bind("<Control-d>", lambda event: center("right"))
	screen.bind("<Control-w>", lambda event: center("up"))
	screen.bind("<Control-x>", lambda event: center("down"))
	screen.bind("<Control-Up>", lambda event: center("h+"))
	screen.bind("<Control-Down>", lambda event: center("h-"))
	screen.bind("<Control-Right>", lambda event: center("w+"))
	screen.bind("<Control-Left>", lambda event: center("w-"))


