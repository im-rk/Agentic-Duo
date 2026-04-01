from app import process_data

def test_process_data():
    raw_data = ["hello", "world"]
    result = process_data(raw_data)
    assert result == ["HELLO", "WORLD"]