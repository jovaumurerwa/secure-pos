def test_root_returns_running_message(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "POS API is running"}
