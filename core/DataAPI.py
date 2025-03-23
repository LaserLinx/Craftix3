root = None
get_globals_func = None
update_them = None
update_color = None
get_globals_func_in_inv = None
add_in_to_elements_list_func = None
get_crafting_arena = None
add_in_to_additional_types_func = None


def set_aitelf(func):
	global add_in_to_elements_list_func
	add_in_to_elements_list_func = func
def set_add_aditional_types_func(func):
	global add_in_to_additional_types_func
	add_in_to_additional_types_func = func
def set_gca(object):
	global get_crafting_arena
	get_crafting_arena = object

def set_root(rt):
	global root
	root = rt
def set_get_global_func(func):
	global get_globals_func
	get_globals_func = func
def set_updating_vars(v_update_them,v_update_color):
	global update_color,update_them
	update_them = v_update_them
	update_color = v_update_color


def set_get_global_func_in_inv(func):
	global get_globals_func_in_inv
	get_globals_func_in_inv = func