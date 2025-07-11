import os
import pytest
from fastapi.testclient import TestClient

from src.app import app

@pytest.fixture(scope="module")
def client(tmp_path, monkeypatch):
    # Monte un petit dossier raw factice
    raw = tmp_path / "data/raw/TestClass"
    raw.mkdir(parents=True)
    # Crée une fausse image
    img_path = raw / "img.png"
    from PIL import Image
    Image.new("RGB", (224,224)).save(img_path)

    # Override RAW_DIR et MODEL_PATH pointent vers des fichiers fixtures
    monkeypatch.setenv("RAW_DIR", str(tmp_path / "data/raw"))
    # On peut aussi créer un dummy model.pth minimal
    from torchvision import models
    import torch, torch.nn as nn
    model = models.resnet18(pretrained=False)
    model.fc = nn.Linear(model.fc.in_features, 1)
    dummy_sd = model.state_dict()
    torch.save(dummy_sd, tmp_path / "model.pth")
    monkeypatch.setenv("MODEL_PATH", str(tmp_path / "model.pth"))

    # Import après monkeypatch
    from importlib import reload
    import src.app
    reload(src.app)

    return TestClient(src.app.app)
