from api import get_user_status_endpoint

def test_get_user_status_endpoint():
    # This test will fail with a KeyError: 'status'
    response = get_user_status_endpoint(1)
    assert response["code"] == 200
    assert response["message"] == "User is active"