from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.services.auth_service import AuthService

router = APIRouter()

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/login")
def login(request: LoginRequest):
    try:
        token_data = AuthService.login(request.email, request.password)
        return token_data
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))
