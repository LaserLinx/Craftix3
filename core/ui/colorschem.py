import json
import os

def load_settings():
	with open("settings.json") as f:
		data = json.loads(f.read())
		f.close()
	return data

settings = load_settings()
them_path = os.path.join("./assets/themes",f"{settings.get("them")}.json")
mode = settings.get("mode")
them = {}
with open(them_path) as f:
    them = json.loads(f.read())
    f.close()

if mode == "light":
    outline_collor = them["CTkFrame"].get("border_color")[0]
    dark_bg_color = them["CTkFrame"].get("fg_color")[0]
    light_bg_color = them["CTkFrame"].get("top_fg_color")[0]
    text_color =them["CTkLabel"].get("text_color")[0]
else:
    outline_collor = them["CTkFrame"].get("border_color")[1]
    dark_bg_color = them["CTkFrame"].get("fg_color")[1]
    light_bg_color = them["CTkFrame"].get("top_fg_color")[1]
    text_color =them["CTkLabel"].get("text_color")[1]