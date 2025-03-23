import time
import random
import threading


green_messages = [
	"System initialized!",
	"Connection established!",
	"Files found and loaded successfully!",
	"Update complete!",
	"Operation successful!",
	"Ready to roll!",
	"App is up and running!"
]

# Červené zprávy
red_messages = [
	"[ERROR] Unable to load configuration!",
	"Error: Missing required file!",
	"Permission denied!",
	"Operation failed. Please try again.",
	"[GENERATOR ERROR] Invalid input detected!",
	"Critical failure! Cannot proceed!",
	"[ERROR] Unable to start server!"
]

# Žluté zprávy
yellow_messages = [
	"[INFO] Checking for updates...",
	"[INFO] Loading user preferences...",
	"[INFO] Preparing environment...",
	"[INFO] Verifying system integrity...",
	"[INFO] Starting background services...",
	"[INFO] Initializing components..."
]

# Kombinování všech zpráv do jednoho seznamu
messages = []
messages += green_messages
messages += red_messages
messages += yellow_messages

# Funkce pro vypsání náhodných zpráv se zpožděním
def print_random_messages():
	random.shuffle(messages)  # Zamíchá seznam zpráv
	while True:
		for message in messages:
			print(message)
			# Pauza mezi zprávami (náhodná, mezi 0.1 a 2.0 sekundami)
			time.sleep(random.uniform(0.01, 0.03))
		
def start_printing():
	t = threading.Thread(target=print_random_messages)
	t.start()
	return True


