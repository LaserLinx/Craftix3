#!/bin/bash

# Name of the scripts
SETUP_SCRIPT="setup.sh"
RUN_SCRIPT="run.sh"

echo "Welcome in Craftix Auto Setup"

# Create the virtual environment
echo "Creating a virtual environment with Python..."
python3 -m venv ./

# Activate the virtual environment
echo "Activating the virtual environment..."
source ./bin/activate

# Install dependencies from requirements.txt
echo "Installing dependencies from requirements.txt..."
pip install -r requirements.txt

# Create the run script
echo "Creating the run script..."
cat <<EOL > $RUN_SCRIPT
#!/bin/bash
source ./bin/activate
python3 main.py
EOL

# Make the run script executable
chmod +x $RUN_SCRIPT

echo "Setup complete! Use ./$RUN_SCRIPT to run the application."

