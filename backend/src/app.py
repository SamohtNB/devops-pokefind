import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from PIL import Image

import torch
import torch.nn as nn
from torchvision import models, transforms

# 1. Initialisation FastAPI
app = FastAPI()

# 2. Paramètres
MODEL_PATH = os.getenv("MODEL_PATH", "model.pth")
RAW_DIR    = os.getenv("RAW_DIR", "data/raw")  # dossier copié dans l'image
device     = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# 3. Détection automatique des classes
if not os.path.isdir(RAW_DIR):
    raise FileNotFoundError(f"Répertoire RAW_DIR introuvable : {RAW_DIR}")
class_names = sorted(
    d for d in os.listdir(RAW_DIR)
    if os.path.isdir(os.path.join(RAW_DIR, d))
)
num_classes = len(class_names)
print(f"Detected {num_classes} classes.")

# 4. Chargement du modèle
model = models.resnet18(pretrained=False)
model.fc = nn.Linear(model.fc.in_features, num_classes)

if not os.path.isfile(MODEL_PATH):
    raise FileNotFoundError(f"Modèle introuvable : {MODEL_PATH}")
state_dict = torch.load(
    MODEL_PATH,
    map_location=device,
    weights_only=False           # <— ajouté pour désactiver le mode weights-only
)
model.load_state_dict(state_dict)
model.to(device)
model.eval()

# 5. Transformations d'entrée
transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406],
                         [0.229, 0.224, 0.225]),
])

# 6. Schéma de requête
class PredictRequest(BaseModel):
    image_path: str  # ou base64, à adapter selon ton front

# 7. Endpoint de prédiction
@app.post("/predict")
def predict(req: PredictRequest):
    # Vérifie que le fichier existe
    if not os.path.isfile(req.image_path):
        raise HTTPException(status_code=400, detail="Image not found")

    # Charge et transforme
    img = Image.open(req.image_path).convert("RGB")
    x = transform(img).unsqueeze(0).to(device)

    # Inférence
    with torch.no_grad():
        outputs = model(x)
        _, pred = torch.max(outputs, 1)

    label = class_names[pred.item()]
    return {"prediction": label}
