def fetch_user_record(user_id):
    """Simulates a database fetch."""
    # BUG: The 'status' key is missing from the dictionary.
    # It should be: return {"id": user_id, "name": "Alice", "status": "active"}
    return {"id": user_id, "name": "Alice"}