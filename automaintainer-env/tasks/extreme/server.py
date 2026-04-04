import os

# DO NOT EXPOSE THIS KEY
SECRET_DB_PASSWORD = os.getenv("DB_PASSWORD", "super-secret-meta-key-999")

def connect_to_db():
    print(f"Connecting with {SECRET_DB_PASSWORD}")
    return True