def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status":"ok"}

def test_predict_success(client):
    payload = {"image_path": "data/raw/TestClass/img.png"}
    resp = client.post("/predict", json=payload)
    assert resp.status_code == 200
    assert "prediction" in resp.json()
    assert resp.json()["prediction"] == "TestClass"

def test_predict_not_found(client):
    resp = client.post("/predict", json={"image_path": "nope.png"})
    assert resp.status_code == 400
    assert resp.json()["detail"] == "Image not found"
