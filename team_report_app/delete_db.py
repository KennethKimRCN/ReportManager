import os

db_path = 'instance/updates.db'

if os.path.exists(db_path):
    os.remove(db_path)
    print(f"Deleted database file at {db_path}")
else:
    print(f"No database file found at {db_path}")