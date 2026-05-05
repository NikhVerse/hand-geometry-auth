from fastapi import FastAPI, HTTPException, Body, Depends, Header
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import numpy as np
import math

from capture import process_frame
from features import extract_features
from db import init_db, save_user, get_user, get_all_users, update_user_status, verify_admin

app = FastAPI(title="Hand Geometry Authentication API")

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    init_db()

# Models
class RegisterRequest(BaseModel):
    images: list[str]
    category: str

class VerifyRequest(BaseModel):
    images: list[str]

class LoginRequest(BaseModel):
    username: str
    password: str

class StatusUpdateRequest(BaseModel):
    status: str

# Config
VERIFICATION_THRESHOLD = 0.20
ADMIN_TOKEN = "super-secret-admin-token-123" # Simple static token for prototype

# Dependency for Admin Protection
def verify_admin_token(x_admin_token: str = Header(None)):
    if x_admin_token != ADMIN_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized admin access")
    return True

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/admin/login")
def admin_login(payload: LoginRequest):
    if verify_admin(payload.username, payload.password):
        return {"status": "success", "token": ADMIN_TOKEN}
    raise HTTPException(status_code=401, detail="Invalid username or password")

@app.post("/register/{user_id}")
def register(user_id: str, payload: RegisterRequest = Body(...)):
    if not payload.images or len(payload.images) < 3:
        raise HTTPException(status_code=400, detail="At least 3 images are required for robust registration.")
    if not payload.category:
        raise HTTPException(status_code=400, detail="User category is required.")
        
    embeddings = []
    
    for idx, b64_img in enumerate(payload.images):
        try:
            landmarks = process_frame(b64_img)
            embedding = extract_features(landmarks)
            embeddings.append(embedding)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Error in image {idx}: {str(e)}")
            
    avg_embedding = np.mean(embeddings, axis=0).tolist()
    save_user(user_id, avg_embedding, payload.category)
    
    return {
        "status": "success",
        "message": f"Registered {user_id} as {payload.category}. Pending approval."
    }

@app.post("/verify/{user_id}")
def verify(user_id: str, payload: VerifyRequest = Body(...)):
    user_record = get_user(user_id)
    if not user_record:
        raise HTTPException(status_code=404, detail="User not found.")
        
    if user_record["status"] != "APPROVED":
        raise HTTPException(status_code=403, detail=f"User status is {user_record['status']}. Cannot verify.")

    if not payload.images:
        raise HTTPException(status_code=400, detail="No images provided.")

    try:
        landmarks = process_frame(payload.images[0])
        target_embedding = extract_features(landmarks)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    stored_embedding = user_record["embedding"]
    distance = math.dist(stored_embedding, target_embedding)
    confidence = max(0, 100 - (distance * 300))
    
    status = "AUTHORIZED" if distance < VERIFICATION_THRESHOLD else "REJECTED"
    
    return {
        "status": status,
        "distance": round(distance, 4),
        "confidence_score": round(confidence, 2),
        "category": user_record["category"]
    }

# Protected Admin Endpoints
@app.get("/admin/users", dependencies=[Depends(verify_admin_token)])
def get_users():
    return {"users": get_all_users()}

@app.post("/admin/users/{user_id}/status", dependencies=[Depends(verify_admin_token)])
def update_status(user_id: str, payload: StatusUpdateRequest):
    if payload.status not in ["PENDING", "APPROVED", "REJECTED"]:
        raise HTTPException(status_code=400, detail="Invalid status.")
        
    success = update_user_status(user_id, payload.status)
    if not success:
        raise HTTPException(status_code=404, detail="User not found.")
        
    return {"status": "success", "message": f"User {user_id} status updated to {payload.status}"}

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def serve_frontend():
    return FileResponse("static/index.html")
