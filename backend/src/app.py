import os
import io
from fastapi import FastAPI, HTTPException, UploadFile, File, Response
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image

import torch
import torch.nn as nn
import torch.serialization
import numpy as np
from torchvision import models, transforms
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST

# 1. Création de l'app
app = FastAPI()

# 2. CORS pour autoriser le front React (localhost:3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Middleware de métriques Prometheus
REQUESTS = Counter(
    "app_requests_total", "Total HTTP requests", ["endpoint", "method", "status"]
)

@app.middleware("http")
async def metrics_middleware(request, call_next):
    response = await call_next(request)
    REQUESTS.labels(
        endpoint=request.url.path,
        method=request.method,
        status=str(response.status_code)
    ).inc()
    return response

@app.get("/metrics")
def metrics():
    data = generate_latest()
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)

# 4. Variables d'environnement pour modèle et classes
MODEL_PATH = os.getenv("MODEL_PATH", "model.pth")
RAW_DIR    = os.getenv("RAW_DIR", "data/raw")
device     = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# 5. Récupération automatique des classes
if not os.path.isdir(RAW_DIR):
    raise FileNotFoundError(f"Répertoire RAW_DIR introuvable : {RAW_DIR}")
class_names = sorted(
    d for d in os.listdir(RAW_DIR)
    if os.path.isdir(os.path.join(RAW_DIR, d))
)
num_classes = len(class_names)
print(f"Detected {num_classes} classes: {class_names[:5]} ...")

# 6. Définition et chargement du modèle
model = models.resnet18(pretrained=False)
model.fc = nn.Linear(model.fc.in_features, num_classes)

if not os.path.isfile(MODEL_PATH):
    raise FileNotFoundError(f"Modèle introuvable : {MODEL_PATH}")

# Autoriser le chargement de numpy arrays
torch.serialization.add_safe_globals([np.core.multiarray._reconstruct])

state_dict = torch.load(
    MODEL_PATH,
    map_location=device,
    weights_only=False
)
# Nettoyage de clés prosélytes si besoin
first_key = next(iter(state_dict))
if first_key.startswith("_orig_mod."):
    state_dict = {k.replace("_orig_mod.", ""): v for k, v in state_dict.items()}

model.load_state_dict(state_dict)
model.to(device)
model.eval()

# 7. Transforms pour l'image
transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406],
                         [0.229, 0.224, 0.225]),
])

@app.get("/health")
def health():
    return {"status": "ok"}

# 8. Endpoint de prédiction recevant un fichier
@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    # Lire l'image en mémoire
    contents = await file.read()
    try:
        img = Image.open(io.BytesIO(contents)).convert("RGB")
    except Exception:
        raise HTTPException(status_code=400, detail="Impossible de lire l'image")

    # Transformation et inférence
    x = transform(img).unsqueeze(0).to(device)
    with torch.no_grad():
        outputs = model(x)
        _, pred = torch.max(outputs, 1)

    return {"prediction": class_names[pred.item()]}  
