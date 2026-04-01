from database import fetch_user_record

def get_user_status_endpoint(user_id):
    """API endpoint to get a user's status."""
    user = fetch_user_record(user_id)
    
    # This will throw a KeyError because 'status' is missing from the DB record
    if user["status"] == "active":
        return {"code": 200, "message": "User is active"}
    return {"code": 403, "message": "User inactive"}