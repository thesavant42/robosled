# config_loader.py
"""
Simple configuration loader for Robot Control System.

This module loads a configuration file (robot_config.txt) where each
line is a key-value pair (key = value) and supports comments starting with '#'.
"""

def load_config(filepath):
    """
    Load configuration parameters from a text file.

    Parameters:
        filepath (str): The path to the configuration file.

    Returns:
        dict: A dictionary with configuration keys and their corresponding values.
    """
    config = {}
    try:
        with open(filepath, "r") as f:
            for line in f:
                line = line.strip()
                # Skip empty lines or comments
                if not line or line.startswith("#"):
                    continue
                # Split key and value on the first '=' encountered.
                if "=" in line:
                    key, value = line.split("=", 1)
                    # Remove extraneous whitespace and any surrounding quotes.
                    config[key.strip()] = value.strip().strip('"')
    except Exception as e:
        print("Error loading config from {}: {}".format(filepath, e))
    
    return config

# When run as a script, print the loaded configuration.
if __name__ == "__main__":
    config_file = "robot_config.txt"
    config = load_config(config_file)
    print("Loaded configuration from {}:".format(config_file))
    for k, v in config.items():
        print("  {} = {}".format(k, v))
