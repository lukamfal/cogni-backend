from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_access_token
from app.core import rate_limit
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserLogin, UserOut, TokenOut

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post("/register", response_model=TokenOut, status_code=201)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="E-mail já cadastrado")

    user = User(
        name=payload.name,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        role=UserRole(payload.role),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(str(user.id))
    return TokenOut(access_token=token, user=UserOut.model_validate(user))


@router.post("/login", response_model=TokenOut)
def login(payload: UserLogin, request: Request, db: Session = Depends(get_db)):
    ip = request.client.host if request.client else "desconhecido"
    if rate_limit.is_blocked(payload.email, ip):
        raise HTTPException(
            status_code=429,
            detail="Muitas tentativas de entrar. Espere 15 minutos e tente de novo.",
        )

    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        rate_limit.register_failure(payload.email, ip)
        raise HTTPException(status_code=401, detail="E-mail ou senha incorretos")

    rate_limit.clear(payload.email)
    token = create_access_token(str(user.id))
    return TokenOut(access_token=token, user=UserOut.model_validate(user))
