from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import mlflow.pytorch
import torch
import os

app = FastAPI()

# Charger le modèle depuis le Model Registry en production
MODEL_URI = "models:/final-project/Production"
model = mlflow.pytorch.load_model(MODEL_URI)
model.eval()

# Classe pour la requête
class PredictRequest(BaseModel):
    # exemple : chemin local de l'image ou base64… adapte selon ton front
    image_path: str

@app.post("/predict")
def predict(req: PredictRequest):
    # 1. Charger et transformer l'image
    from PIL import Image
    from torchvision import transforms

    img = Image.open(req.image_path).convert("RGB")
    tf = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize([0.485,0.456,0.406],[0.229,0.224,0.225])
    ])
    x = tf(img).unsqueeze(0)

    # 2. Prédiction
    with torch.no_grad():
        outputs = model(x)
        _, pred = torch.max(outputs, 1)

    # 3. Retourner l’indice (ou le nom de la classe)
    preds = model.metadata.get("class_names", None)
    label = preds[pred.item()] if preds else str(pred.item())
    return {"prediction": label}
