import json

def trim_pattern(pattern):
	while pattern and all(c == ' ' for c in pattern[0]):
		pattern.pop(0)
	while pattern and all(c == ' ' for c in pattern[-1]):
		pattern.pop(-1)

	if not pattern:
		return pattern
	min_col = min(len(row) - len(row.lstrip(' ')) for row in pattern)
	max_col = max(len(row.rstrip(' ')) for row in pattern)

	trimmed_pattern = [row[min_col:max_col] for row in pattern]
	return trimmed_pattern

def generate_minecraft_recipe(data):
	grid = ["   ", "   ", "   "]
	key_mapping = {}
	item_to_key = {}
	next_key = 'a'

	for pos, item in data['crafting'].items():
		if item not in item_to_key:
			
			print(item)
			if str(item).startswith("tag:"):
				item = str(item).replace("¶",":")
				item = str(item).replace("ŧ","/")
				item = str(item).replace("tag:","")
				item_to_key[item] = next_key
				key_mapping[next_key] = {"tag": item}
			else:
				item_to_key[item] = next_key
				key_mapping[next_key] = {"item": item}
			next_key = chr(ord(next_key) + 1)
		print(item)
		row, col = divmod(int(pos) - 1, 3)
		grid[row] = grid[row][:col] + item_to_key[item] + grid[row][col+1:]

	trimmed_pattern = trim_pattern(grid)

	recipe = {
		"type": "minecraft:crafting_shaped",
		"acceptMirrored": True,
		"pattern": trimmed_pattern,
		"key": key_mapping,
		"result": {
			"item": data['result'],
			"count": int(data['result_count'])
		}
	}

	return json.dumps(recipe)
def generate_minecraft_mechanical_crafting_recipe(data):
	# Inicializace 9x9 mřížky pro mechanical crafting
	grid_size = 9
	grid = [" " * grid_size for _ in range(grid_size)]
	key_mapping = {}
	item_to_key = {}
	next_key = 'a'

	for pos, item in data['crafting'].items():
		if item not in item_to_key:
			if str(item).startswith("tag:"):
				item = str(item).replace("¶",":")
				item = str(item).replace("ŧ","/")
				item = str(item).replace("tag:","")
				item_to_key[item] = next_key
				key_mapping[next_key] = {"tag": item}
			else:
				item_to_key[item] = next_key
				key_mapping[next_key] = {"item": item}
			next_key = chr(ord(next_key) + 1)
		
		row, col = divmod(int(pos) - 1, grid_size)
		grid[row] = grid[row][:col] + item_to_key[item] + grid[row][col+1:]

	# Trim the grid
	trimmed_pattern = trim_pattern(grid)

	# Construct the JSON structure
	recipe = {
		"type": "create:mechanical_crafting",
		"acceptMirrored": True,
		"pattern": trimmed_pattern,
		"key": key_mapping,
		"result": {
			"item": data['result'],
			"count": int(data['result_count'])
		}
	}

	return json.dumps(recipe)

def generate_minecraft_furnace(data):
	recipe = {}
	recipe["type"] = str(data.get("furnace_type"))
	recipe["cookingtime"] = int(data.get("cookingtime"))
	recipe["experience"] = float(data.get("experience"))
	recipe["ingredient"] = {}
	item = str(data.get("in"))
	if str(item).startswith("tag:"):
		item = str(item).replace("¶",":")
		item = str(item).replace("ŧ","/")
		item = str(item).replace("tag:","")
		recipe["ingredient"]["tag"] = item
	else:
		recipe["ingredient"]["item"] = item
	recipe["result"] = {}
	recipe["result"]["item"] = str(data.get("result"))
	recipe["result"]["count"] = int(data.get("result_count"))
	return json.dumps(recipe)


def generate_create_pressing(data):
	recipe = {}
	recipe["type"] = "create:pressing"
	recipe["ingredients"] = []
	item = str(data.get("in"))
	if str(item).startswith("tag:"):
		item = str(item).replace("¶",":")
		item = str(item).replace("ŧ","/")
		item = str(item).replace("tag:","")
		in_json = {"tag": item}
	else:
		in_json = {"item": item}
	recipe["ingredients"].append(in_json)
	recipe["results"] = []
	results = data.get("results")
	for result in results:
		recipe["results"].append({"item":str(result.get("item")),"count": int(result.get("count")),"chance": float(float(result.get("chance")) / 100.0)})
	return json.dumps(recipe)

def generate_crafting_shapless(data):
	recipe = {}
	recipe["type"] = "crafting_shapeless"
	recipe["result"] = {}
	recipe["result"]["item"] = str(data.get("result"))
	recipe["result"]["count"] = int(data.get("result_count"))
	recipe["ingredients"] = []
	inputs = []
	keys = data.get("crafting").keys()
	for key in keys:
		item = str(data["crafting"].get(key))
		json_input = {}
		if str(item).startswith("tag:"):
			item = str(item).replace("¶",":")
			item = str(item).replace("ŧ","/")
			item = str(item).replace("tag:","")
			json_input["tag"] = item
		else:
			json_input["item"] = item
		inputs.append(json_input)
	recipe["ingredients"] = inputs
	return json.dumps(recipe)

def generate_stonecutting(data):
	recipe = {}
	recipe["type"] = "minecraft:stonecutting"
	recipe["count"] = int(data.get("result_count"))
	recipe["result"] = str(data.get("result"))
	json_input = {}
	item = data.get("in")
	if str(item).startswith("tag:"):
		item = str(item).replace("¶",":")
		item = str(item).replace("ŧ","/")
		item = str(item).replace("tag:","")
		json_input["tag"] = item
	else:
		json_input["item"] = item
	recipe["ingredient"] = json_input
	return json.dumps(recipe)

def generate_smithing(data):
	recipe = {}
	recipe["type"] = "minecraft:smithing_transform"
	recipe["result"] = {}
	recipe["result"]["item"] = str(data.get("result"))
	json_input = {}
	item = data.get("in")
	if str(item).startswith("tag:"):
		item = str(item).replace("¶",":")
		item = str(item).replace("ŧ","/")
		item = str(item).replace("tag:","")
		json_input["tag"] = item
	else:
		json_input["item"] = item
	json_addition = {}
	item = data.get("addition")
	if str(item).startswith("tag:"):
		item = str(item).replace("¶",":")
		item = str(item).replace("ŧ","/")
		item = str(item).replace("tag:","")
		json_addition["tag"] = item
	else:
		json_addition["item"] = item
	json_inputtemplate = {}
	item = data.get("inpatern")
	if str(item).startswith("tag:"):
		item = str(item).replace("¶",":")
		item = str(item).replace("ŧ","/")
		item = str(item).replace("tag:","")
		json_inputtemplate["tag"] = item
	else:
		json_inputtemplate["item"] = item
	recipe["addition"] = json_addition
	recipe["base"] = json_input
	recipe["template"] = json_inputtemplate
	return json.dumps(recipe)

def generate_custum_json(data):
	recipe = data.get("json")
	return json.dumps(recipe)


def generate_crate_mixing(data):
#	data = {}
	recipe = {}
	recipe["type"] = "create:mixing"
	recipe["heatRequirement"] = str(data.get("hated"))
	#input
	recipe["ingredients"] = []
	if not data.get("ins_fluid1") == "":
		recipe["ingredients"].append({"fluid": str(data.get("ins_fluid1")),"amount": int(data.get("fluids_parms").get('1'))})
	if not data.get("ins_fluid2") == "":
		recipe["ingredients"].append({"fluid": str(data.get("ins_fluid2")),"amount": int(data.get("fluids_parms").get('2'))})
	
	#output
	recipe["results"] = []
	if not data.get("results_fluids1") == "":
		recipe["results"].append({"fluid": str(data.get("results_fluids1")),"amount": int(data.get("fluids_parms").get('3')),"chance": float(float(data.get("fluids_parms").get('4')) / 100)})
	if not data.get("results_fluids2") == "":
		recipe["results"].append({"fluid": str(data.get("results_fluids2")),"amount": int(data.get("fluids_parms").get('5')),"chance": float(float(data.get("fluids_parms").get('6')) / 100)})
	ins_items = data.get("ins_items")
	ins_keys = ins_items.keys()
	for key in ins_keys:
		item = ins_items.get(key)
		if not item == "":
			count = int(data.get("ins_items_count").get(key))
			for _ in range (0,count):
				item = ins_items.get(key)
				print(item)
				if str(item).startswith("tag:"):
					item = str(item).replace("¶",":")
					item = str(item).replace("ŧ","/")
					item = str(item).replace("tag:","")
					recipe["ingredients"].append({"tag": str(item)})
				else:
					recipe["ingredients"].append({"item": str(item)})
	
	result_items = data.get("results_items")
	result_items_keys = result_items.keys()
	for key in result_items_keys:
		item = result_items.get(key)
		if not item == "":
			count = data.get("results_items_count").get(key)
			chance = data.get("results_items_chance").get(key)
			recipe["results"].append({"item": str(item),"count": int(count),"chance": float(float(chance) / 100)})
		
	
	
	#return json
	return json.dumps(recipe)



def generate_create_compacting(data):
#	data = {}
	recipe = {}
	recipe["type"] = "create:compacting"
	recipe["heatRequirement"] = str(data.get("hated"))
	#input
	recipe["ingredients"] = []
	if not data.get("ins_fluid1") == "":
		recipe["ingredients"].append({"fluid": str(data.get("ins_fluid1")),"amount": int(data.get("fluids_parms").get('1'))})
	if not data.get("ins_fluid2") == "":
		recipe["ingredients"].append({"fluid": str(data.get("ins_fluid2")),"amount": int(data.get("fluids_parms").get('2'))})
	
	#output
	recipe["results"] = []
	if not data.get("results_fluids1") == "":
		recipe["results"].append({"fluid": str(data.get("results_fluids1")),"amount": int(data.get("fluids_parms").get('3')),"chance": float(float(data.get("fluids_parms").get('4')) / 100)})
	if not data.get("results_fluids2") == "":
		recipe["results"].append({"fluid": str(data.get("results_fluids2")),"amount": int(data.get("fluids_parms").get('5')),"chance": float(float(data.get("fluids_parms").get('6')) / 100)})
	ins_items = data.get("ins_items")
	ins_keys = ins_items.keys()
	for key in ins_keys:
		item = ins_items.get(key)
		if not item == "":
			count = int(data.get("ins_items_count").get(key))
			for _ in range (0,count):
				item = ins_items.get(key)
				print(item)
				if str(item).startswith("tag:"):
					item = str(item).replace("¶",":")
					item = str(item).replace("ŧ","/")
					item = str(item).replace("tag:","")
					recipe["ingredients"].append({"tag": str(item)})
				else:
					recipe["ingredients"].append({"item": str(item)})
	
	result_items = data.get("results_items")
	result_items_keys = result_items.keys()
	for key in result_items_keys:
		item = result_items.get(key)
		if not item == "":
			count = data.get("results_items_count").get(key)
			chance = data.get("results_items_chance").get(key)
			recipe["results"].append({"item": str(item),"count": int(count),"chance": float(float(chance) / 100)})
		
	
	
	#return json
	return json.dumps(recipe)

def generate_create_item_application(data):
	recipe = {}
	recipe["type"] = "create:item_application"
	recipe["ingredients"] = []
	recipe["results"] = []
	consumed = int(data.get("consument"))
	if consumed == 1:
		recipe["keepHeldItem"] = False
	else:
		recipe["keepHeldItem"] = True

	item = data.get("in")
	if str(item).startswith("tag:"):
		item = str(item).replace("¶",":")
		item = str(item).replace("ŧ","/")
		item = str(item).replace("tag:","")
		recipe["ingredients"].append({"tag": str(item)})
	else:
		recipe["ingredients"].append({"item": str(item)})

	item = data.get("sub_in")
	if str(item).startswith("tag:"):
		item = str(item).replace("¶",":")
		item = str(item).replace("ŧ","/")
		item = str(item).replace("tag:","")
		recipe["ingredients"].append({"tag": str(item)})
	else:
		recipe["ingredients"].append({"item": str(item)})
	results = data.get("results")
	for result in results:
		recipe["results"].append({"item":str(result.get("item")),"count": int(result.get("count")),"chance": float(float(result.get("chance")) / 100.0)})

	return json.dumps(recipe)

def generate_create_deployng(data):
	recipe = {}
	recipe["type"] = "create:deploying"
	recipe["ingredients"] = []
	recipe["results"] = []
	consumed = int(data.get("consument"))
	if consumed == 1:
		recipe["keepHeldItem"] = False
	else:
		recipe["keepHeldItem"] = True

	item = data.get("in")
	if str(item).startswith("tag:"):
		item = str(item).replace("¶",":")
		item = str(item).replace("ŧ","/")
		item = str(item).replace("tag:","")
		recipe["ingredients"].append({"tag": str(item)})
	else:
		recipe["ingredients"].append({"item": str(item)})

	item = data.get("sub_in")
	if str(item).startswith("tag:"):
		item = str(item).replace("¶",":")
		item = str(item).replace("ŧ","/")
		item = str(item).replace("tag:","")
		recipe["ingredients"].append({"tag": str(item)})
	else:
		recipe["ingredients"].append({"item": str(item)})
	results = data.get("results")
	for result in results:
		recipe["results"].append({"item":str(result.get("item")),"count": int(result.get("count")),"chance": float(float(result.get("chance")) / 100.0)})

	return json.dumps(recipe)

def generate_create_crushing(data):
	recipe = {}
	recipe["type"] = "create:crushing"
	recipe["ingredients"] = []
	item = str(data.get("in"))
	if str(item).startswith("tag:"):
		item = str(item).replace("¶",":")
		item = str(item).replace("ŧ","/")
		item = str(item).replace("tag:","")
		in_json = {"tag": item}
	else:
		in_json = {"item": item}
	recipe["ingredients"].append(in_json)
	recipe["processingTime"] = int(int(data.get("time")) * 20)
	recipe["results"] = []
	results = data.get("results")
	for result in results:
		recipe["results"].append({"item":str(result.get("item")),"count": int(result.get("count")),"chance": float(float(result.get("chance")) / 100.0)})
	return json.dumps(recipe)


def generate_create_milling(data):
	recipe = {}
	recipe["type"] = "create:milling"
	recipe["ingredients"] = []
	item = str(data.get("in"))
	if str(item).startswith("tag:"):
		item = str(item).replace("¶",":")
		item = str(item).replace("ŧ","/")
		item = str(item).replace("tag:","")
		in_json = {"tag": item}
	else:
		in_json = {"item": item}
	recipe["ingredients"].append(in_json)
	recipe["processingTime"] = int(int(data.get("time")) * 20)
	recipe["results"] = []
	results = data.get("results")
	for result in results:
		recipe["results"].append({"item":str(result.get("item")),"count": int(result.get("count")),"chance": float(float(result.get("chance")) / 100.0)})
	return json.dumps(recipe)


def generate_create_cutting(data):
	recipe = {}
	recipe["type"] = "create:cutting"
	recipe["ingredients"] = []
	item = str(data.get("in"))
	if str(item).startswith("tag:"):
		item = str(item).replace("¶",":")
		item = str(item).replace("ŧ","/")
		item = str(item).replace("tag:","")
		in_json = {"tag": item}
	else:
		in_json = {"item": item}
	recipe["ingredients"].append(in_json)
	recipe["processingTime"] = int(int(data.get("time")) * 20)
	recipe["results"] = []
	results = data.get("results")
	for result in results:
		recipe["results"].append({"item":str(result.get("item")),"count": int(result.get("count")),"chance": float(float(result.get("chance")) / 100.0)})
	return json.dumps(recipe)

def generate_vortex(data):
	return str(data.get("vortex"))


def generate_create_filling(data):
	recipe = {}
	recipe["type"] = "create:filling"
	recipe["ingredients"] = []
	item = str(data.get("subin"))
	if str(item).startswith("tag:"):
		item = str(item).replace("¶",":")
		item = str(item).replace("ŧ","/")
		item = str(item).replace("tag:","")
		in_json = {"tag": item}
	else:
		in_json = {"item": item}
	recipe["ingredients"].append(in_json)
	item = str(data.get("in"))
	if str(item).startswith("tag:"):
		item = str(item).replace("¶",":")
		item = str(item).replace("ŧ","/")
		item = str(item).replace("tag:","")
		in_json = {"fluid": item,"amount": int(data.get("amount"))}
	else:
		in_json = {"fluid": item,"amount": int(data.get("amount"))}
	recipe["ingredients"].append(in_json)	
	recipe["results"] = []
	results = data.get("results")
	for result in results:
		recipe["results"].append({"item":str(result.get("item")),"count": int(result.get("count")),"chance": float(float(result.get("chance")) / 100.0)})
	return json.dumps(recipe)

def generate_create_sequence_assembly(data):
	recipe = {}
	recipe["type"] = "create:sequenced_assembly"
	recipe["loops"] = int(data.get("loops"))
	recipe["transitionalItem"] = {"item": data.get("transitionalItem")}
	item = str(data.get("in"))
	if str(item).startswith("tag:"):
		item = str(item).replace("¶",":")
		item = str(item).replace("ŧ","/")
		item = str(item).replace("tag:","")
		in_json = {"tag": item}
	else:
		in_json = {"item": item}
	recipe["ingredient"] = in_json

	recipe["sequence"] = []
	seq_list = data["sequence"].keys()
	for seq in seq_list:
		rec = {}
		el = data["sequence"].get(seq)
		if el.get("type") == "pressing":#ok
			rec["type"] = "create:pressing"
			rec["ingredients"] = [{"item": data.get("transitionalItem")}]
			rec["results"] = [{"item": data.get("transitionalItem")}]
		
		elif el.get("type") == "cutting":#ok
			rec["type"] = "create:cutting"
			rec["ingredients"] = [{"item": data.get("transitionalItem")}]
			rec["processingTime"] = int(int(el.get("processtime")) * 20)
			rec["results"] = [{"item": data.get("transitionalItem")}]
		
		elif el.get("type") == "deployng":#ok
			rec["type"] = "create:deploying"
			rec["ingredients"] = [{"item": data.get("transitionalItem")},{"item": el.get("subitem")}]
			rec["results"] = [{"item": data.get("transitionalItem")}]
			if el.get("ussage") == True:
				rec["keepHeldItem"] = False
			else:
				rec["keepHeldItem"] = True

		elif el.get("type") == "spouting":#ok
			rec["type"] = "create:filling"
			rec["ingredients"] = [{"item": data.get("transitionalItem")},{"fluid": el.get("fluid"),"amount": int(el.get("amount"))}]
			rec["results"] = [{"item": data.get("transitionalItem")}]
		if not rec == {}:
			recipe["sequence"].append(rec)


	recipe["results"] = []
	results = data.get("results")
	for result in results:
		recipe["results"].append({"item":str(result.get("item")),"count": int(result.get("count")),"chance": float(float(result.get("chance")) / 100.0)})
	return json.dumps(recipe)
