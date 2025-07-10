import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from PIL import Image

import torch
import torch.nn as nn
import torch.serialization
import numpy as np
from torchvision import models, transforms

# 1. Création de l’app
app = FastAPI()

# 2. Variables d’environnement
MODEL_PATH = os.getenv("MODEL_PATH", "model.pth")
RAW_DIR    = os.getenv("RAW_DIR", "data/raw")
device     = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# 3. Récupération automatique des classes
if not os.path.isdir(RAW_DIR):
    raise FileNotFoundError(f"Répertoire RAW_DIR introuvable : {RAW_DIR}")
class_names = sorted(
    d for d in os.listdir(RAW_DIR)
    if os.path.isdir(os.path.join(RAW_DIR, d))
)
num_classes = len(class_names)
print(f"Detected {num_classes} classes: {class_names[:5]} ...")

# 4. Définition du modèle
model = models.resnet18(pretrained=False)
model.fc = nn.Linear(model.fc.in_features, num_classes)

# 5. Chargement du state_dict en autorisant numpy._core.multiarray._reconstruct
if not os.path.isfile(MODEL_PATH):
    raise FileNotFoundError(f"Modèle introuvable : {MODEL_PATH}")

# Add safe global for numpy unpickling
torch.serialization.add_safe_globals([np.core.multiarray._reconstruct])

state_dict = torch.load(
    MODEL_PATH,
    map_location=device,
    weights_only=False
)

first_key = next(iter(state_dict))
if first_key.startswith("_orig_mod."):
    new_dict = {
        k.replace("_orig_mod.", ""): v
        for k, v in state_dict.items()
    }
    state_dict = new_dict

# 2) On peut charger en mode strict
model.load_state_dict(state_dict)
model.to(device)
model.eval()

# 6. Préparation des transforms
transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406],
                         [0.229, 0.224, 0.225]),
])

# 7. Schéma de la requête
class PredictRequest(BaseModel):
    image_path: str

# 8. Endpoint de prédiction
@app.post("/predict")
def predict(req: PredictRequest):
    # Vérification de l’existence du fichier
    if not os.path.isfile(req.image_path):
        raise HTTPException(status_code=400, detail="Image not found")

    # Chargement et transformation
    img = Image.open(req.image_path).convert("RGB")
    x = transform(img).unsqueeze(0).to(device)

    # Inférence
    with torch.no_grad():
        outputs = model(x)
        _, pred = torch.max(outputs, 1)

    return {"prediction": class_names[pred.item()]}
