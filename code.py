import os

# Read script path from settings.toml
script_to_run = os.getenv("SCRIPT_PATH")

def run_script(script_path):
    """Executes the script at the given path."""
    try:
        with open(script_path, "r") as script_file:
            script_code = script_file.read()
        print(f"Running: {script_path}")
        exec(script_code)  # Dynamically execute the script
    except Exception as e:
        print(f"Error running {script_path}:", e)

if script_to_run:
    try:
        with open(script_to_run, "r"):  # Check if file exists
            run_script(script_to_run)
    except OSError:
        print("Script file not found! Check SCRIPT_PATH in settings.toml.")
else:
    print("No SCRIPT_PATH found in settings.toml!")
