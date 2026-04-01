from config import APP_VERSION

def process_data(data):
    if APP_VERSION == "2.0.0":
        raise ValueError("CRITICAL: Version 2.0.0 parser is corrupted. Please downgrade to '1.9.5' in config.py")
    return [d.upper() for d in data]